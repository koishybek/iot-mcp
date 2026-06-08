import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

// ── Configuration ──────────────────────────────────────────────────────────
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const API_BASE_URL = process.env.SM_API_URL || "https://sm.iot-exp.kz";
const API_TOKEN = process.env.SM_API_TOKEN || "";

// ── Load OpenAPI spec ──────────────────────────────────────────────────────
const specRaw = readFileSync(join(__dirname, "openapi"), "utf-8");
const spec = JSON.parse(specRaw);

// ── Create MCP Server ──────────────────────────────────────────────────────
const server = new McpServer({
  name: "smart-metrix",
  version: "1.0.0",
  description: "MCP-сервер для Smart Metrix IoT API. Только GET-запросы для чтения данных системы учёта ресурсов.",
});

// ── Helper: make authenticated GET request ─────────────────────────────────
async function apiGet(path, queryParams = {}) {
  const url = new URL(path, API_BASE_URL);

  for (const [key, value] of Object.entries(queryParams)) {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  }

  const headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
  };

  if (API_TOKEN) {
    headers["Authorization"] = `Token ${API_TOKEN}`;
  }

  const response = await fetch(url.toString(), { headers });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error");
    throw new Error(`API request failed: ${response.status} ${response.statusText} — ${errorText}`);
  }

  // Some endpoints return files (e.g. downloads), handle gracefully
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return { status: response.status, message: `Non-JSON response (${contentType})`, statusText: response.statusText };
  }

  return await response.json();
}

// ── Helper: convert OpenAPI param type to Zod schema ───────────────────────
function paramToZod(param) {
  let schema;
  const type = param.type || "string";

  if (type === "integer") {
    schema = z.number().int();
  } else if (type === "number") {
    schema = z.number();
  } else if (type === "boolean") {
    schema = z.boolean();
  } else {
    // string (possibly with enum)
    if (param.enum && param.enum.length > 0) {
      schema = z.enum(param.enum);
    } else {
      schema = z.string();
    }
  }

  // All params are optional for query, required for path
  if (!param.required) {
    schema = schema.optional();
  }

  // Add description
  const desc = param.description || param.name;
  if (desc) {
    schema = schema.describe(desc);
  }

  return schema;
}

// ── Extract GET endpoints from spec ────────────────────────────────────────
function extractGetEndpoints() {
  const endpoints = [];

  for (const [path, methods] of Object.entries(spec.paths)) {
    if (!methods.get) continue;

    const getOp = methods.get;
    const pathParams = methods.parameters || [];

    // Merge path-level params with operation-level params
    const allParams = [...pathParams, ...(getOp.parameters || [])];

    endpoints.push({
      path,
      operationId: getOp.operationId,
      description: getOp.description || "",
      parameters: allParams,
    });
  }

  return endpoints;
}

// ── Register all GET endpoints as MCP tools ────────────────────────────────
const endpoints = extractGetEndpoints();

for (const endpoint of endpoints) {
  const { path, operationId, description, parameters } = endpoint;

  // Build Zod shape for parameters
  const shape = {};
  for (const param of parameters) {
    shape[param.name] = paramToZod(param);
  }

  // Build a human-readable description
  const paramDescriptions = parameters
    .map((p) => {
      const req = p.required ? "(required)" : "(optional)";
      const enumStr = p.enum ? ` [${p.enum.join(", ")}]` : "";
      return `  - ${p.name}: ${p.description || p.type || "string"} ${req}${enumStr}`;
    })
    .join("\n");

  const toolDescription = [
    description || `GET ${path}`,
    "",
    `Endpoint: GET ${path}`,
    paramDescriptions ? `\nParameters:\n${paramDescriptions}` : "",
  ]
    .filter(Boolean)
    .join("\n");

  // Register tool
  server.tool(
    operationId,
    toolDescription,
    shape,
    async (args) => {
      try {
        // Replace path parameters in the URL
        let resolvedPath = path;
        const queryParams = {};

        for (const param of parameters) {
          const value = args[param.name];
          if (value === undefined || value === null) continue;

          if (param.in === "path") {
            resolvedPath = resolvedPath.replace(`{${param.name}}`, String(value));
          } else if (param.in === "query") {
            queryParams[param.name] = value;
          }
        }

        const result = await apiGet(resolvedPath, queryParams);

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );
}

// ── Start server ───────────────────────────────────────────────────────────
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`Smart Metrix MCP server started. Registered ${endpoints.length} GET tools.`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
