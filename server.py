import json
import os
import httpx
from fastmcp import FastMCP

# ── Configuration ───────────────────────────────────────────────────────────
API_BASE_URL = "https://sm.iot-exp.kz"
API_TOKEN = "fc186709d0cf8bfa4bf5d8567c2456c3178abb51"

SPEC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openapi")

mcp = FastMCP(
    "Smart Metrix",
    instructions="MCP-сервер для IoT-платформы Smart Metrix (sm.iot-exp.kz). Только GET-запросы для чтения данных системы учёта ресурсов.",
)

# ── HTTP Client ─────────────────────────────────────────────────────────────

def api_get(path: str, query_params: dict | None = None) -> dict:
    """Make an authenticated GET request to the Smart Metrix API."""
    url = f"{API_BASE_URL}{path}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {API_TOKEN}",
    }
    params = {}
    if query_params:
        params = {k: v for k, v in query_params.items() if v is not None and v != ""}

    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=headers, params=params)

    if resp.status_code >= 400:
        return {"error": True, "status": resp.status_code, "detail": resp.text[:1000]}

    content_type = resp.headers.get("content-type", "")
    if "application/json" not in content_type:
        return {"status": resp.status_code, "message": f"Non-JSON response ({content_type})"}

    return resp.json()


# ═══════════════════════════════════════════════════════════════════════════
#  ADDRESSES — Адреса
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def address_list(
    ordering: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список адресов. Поддерживает поиск, сортировку и пагинацию."""
    params = {}
    if ordering: params["ordering"] = ordering
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/address/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def address_read(id: int) -> str:
    """Получить детальную информацию об адресе по ID."""
    return json.dumps(api_get(f"/api/v1/address/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  DATA STORE — Хранилище обработанных данных
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def data_store_list(
    meter_id: int = 0,
    diff_reading_period: str = "",
    dt__gte: str = "",
    dt__lte: str = "",
) -> str:
    """Получить обработанные данные из хранилища.
    meter_id (required): ID измерителя.
    diff_reading_period (required): Период агрегации — 'hourly', 'dayly', 'monthly'.
    dt__gte: Дата начала (формат: YYYY-MM-DD HH:MM).
    dt__lte: Дата окончания (формат: YYYY-MM-DD HH:MM).
    """
    params = {}
    if meter_id: params["meter_id"] = meter_id
    if diff_reading_period: params["diff_reading_period"] = diff_reading_period
    if dt__gte: params["dt__gte"] = dt__gte
    if dt__lte: params["dt__lte"] = dt__lte
    return json.dumps(api_get("/api/v1/data_store/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def data_store_read(id: int) -> str:
    """Получить запись хранилища данных по ID."""
    return json.dumps(api_get(f"/api/v1/data_store/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  DATA STORE DEFAULT — Сырые (необработанные) данные
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def data_store_default_list(
    ordering: str = "",
    dt__gte: str = "",
    dt__lte: str = "",
    dt__date__gte: str = "",
    dt__date__lte: str = "",
    dt__date__gt: str = "",
    dt__date__lt: str = "",
    device: str = "",
    meter: str = "",
    gateway: str = "",
    node: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
    distinct: str = "",
) -> str:
    """Получить необработанные (сырые) данные из хранилища.
    Фильтры по дате, устройству, измерителю, шлюзу, узлу.
    distinct: Вернуть последнюю запись для каждого 'device', 'meter' или 'gateway'.
    """
    params = {}
    if ordering: params["ordering"] = ordering
    if dt__gte: params["dt__gte"] = dt__gte
    if dt__lte: params["dt__lte"] = dt__lte
    if dt__date__gte: params["dt__date__gte"] = dt__date__gte
    if dt__date__lte: params["dt__date__lte"] = dt__date__lte
    if dt__date__gt: params["dt__date__gt"] = dt__date__gt
    if dt__date__lt: params["dt__date__lt"] = dt__date__lt
    if device: params["device"] = device
    if meter: params["meter"] = meter
    if gateway: params["gateway"] = gateway
    if node: params["node"] = node
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    if distinct: params["distinct"] = distinct
    return json.dumps(api_get("/api/v1/data_store_default/", params), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  DEVICES — Устройства
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def device_list(
    type: str = "",
    node_service_company: str = "",
    gateway: str = "",
    network_server: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
    eui: str = "",
    report: str = "",
) -> str:
    """Получить список устройств. Фильтры: тип, шлюз, сетевой сервер, EUI.
    eui: Фильтр по EUI (частичное совпадение).
    report: 'get_passports' — скачать паспорта устройств.
    """
    params = {}
    if type: params["type"] = type
    if node_service_company: params["node_service_company"] = node_service_company
    if gateway: params["gateway"] = gateway
    if network_server: params["network_server"] = network_server
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    if eui: params["eui"] = eui
    if report: params["report"] = report
    return json.dumps(api_get("/api/v1/device/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def device_read(id: int) -> str:
    """Получить детальную информацию об устройстве по ID."""
    return json.dumps(api_get(f"/api/v1/device/{id}/"), ensure_ascii=False, indent=2)


@mcp.tool()
def device_mode_list(
    ordering: str = "",
    device_model: str = "",
    meters__id: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список режимов работы устройств."""
    params = {}
    if ordering: params["ordering"] = ordering
    if device_model: params["device_model"] = device_model
    if meters__id: params["meters__id"] = meters__id
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/device/mode/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def device_mode_read(id: int) -> str:
    """Получить режим работы устройства по ID."""
    return json.dumps(api_get(f"/api/v1/device/mode/{id}/"), ensure_ascii=False, indent=2)


@mcp.tool()
def device_model_list(
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список моделей устройств."""
    params = {}
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/device/model/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def device_model_read(id: int) -> str:
    """Получить модель устройства по ID."""
    return json.dumps(api_get(f"/api/v1/device/model/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  DOWNLOADS — Скачивание файлов
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def downloads_read(task_id: str) -> str:
    """Проверить статус и скачать файл по ID задачи.
    200 — файл готов, 202 — ещё выполняется, 410 — не найден.
    """
    return json.dumps(api_get(f"/api/v1/downloads/{task_id}"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  EVENTS — События
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def event_list(
    type: str = "",
    relevant: str = "",
    search: str = "",
    ordering: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список событий. Фильтры: тип, релевантность, поиск, сортировка."""
    params = {}
    if type: params["type"] = type
    if relevant: params["relevant"] = relevant
    if search: params["search"] = search
    if ordering: params["ordering"] = ordering
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/event/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def event_type_list(
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список типов событий."""
    params = {}
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/event_type/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def event_type_read(id: int) -> str:
    """Получить тип события по ID."""
    return json.dumps(api_get(f"/api/v1/event_type/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  GATEWAYS — Шлюзы
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def gateway_list(
    network_server: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список шлюзов. Фильтр по сетевому серверу."""
    params = {}
    if network_server: params["network_server"] = network_server
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/gateway/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def gateway_read(id: int) -> str:
    """Получить информацию о шлюзе по ID."""
    return json.dumps(api_get(f"/api/v1/gateway/{id}/"), ensure_ascii=False, indent=2)


@mcp.tool()
def gateway_stats(id: int) -> str:
    """Получить детальную статистику шлюза: активность, сигнал, количество устройств."""
    return json.dumps(api_get(f"/api/v1/gateway/{id}/stats/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  INSTALLATION PLACES — Места установки
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def installation_place_list(
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список мест установки."""
    params = {}
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/installation_place/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def installation_place_read(id: int) -> str:
    """Получить место установки по ID."""
    return json.dumps(api_get(f"/api/v1/installation_place/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  LOCATION — Геолокация счётчиков
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def location_list(
    search: str = "",
    page: int = 0,
    page_size: int = 0,
    node_id: int = 0,
    zoom: int = 0,
    bounds: str = "",
) -> str:
    """Получить местоположение счётчиков на карте (с кластеризацией).
    node_id: Фильтр по узлу.
    zoom: Масштаб карты (по умолчанию 10).
    bounds: Границы карты JSON: [[lat_min,lng_min],[lat_max,lng_max]].
    """
    params = {}
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    if node_id: params["node_id"] = node_id
    if zoom: params["zoom"] = zoom
    if bounds: params["bounds"] = bounds
    return json.dumps(api_get("/api/v1/location/", params), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  METERS — Измерители (счётчики)
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def meter_list(
    sent_date__gte: str = "",
    sent_date__lte: str = "",
    sent_date: str = "",
    sent_date__gt: str = "",
    sent_date__lt: str = "",
    sent_date__isnull: str = "",
    resource_type: str = "",
    object_type: str = "",
    installation_place: str = "",
    type: str = "",
    is_active: str = "",
    client_sector: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
    node_id: int = 0,
    reading_date: str = "",
    report: str = "",
    columns: str = "",
) -> str:
    """Получить список измерителей (счётчиков).
    Фильтры: тип ресурса, активность, дата показания, тип объекта, сектор.
    node_id: Фильтр по узлу (включает потомков).
    reading_date: Дата показания ISO 8601 — возвращает ближайшее к дате показание.
    report: Тип отчёта ('default_report' или 'custom').
    columns: Колонки для default_report через запятую.
    """
    params = {}
    if sent_date__gte: params["sent_date__gte"] = sent_date__gte
    if sent_date__lte: params["sent_date__lte"] = sent_date__lte
    if sent_date: params["sent_date"] = sent_date
    if sent_date__gt: params["sent_date__gt"] = sent_date__gt
    if sent_date__lt: params["sent_date__lt"] = sent_date__lt
    if sent_date__isnull: params["sent_date__isnull"] = sent_date__isnull
    if resource_type: params["resource_type"] = resource_type
    if object_type: params["object_type"] = object_type
    if installation_place: params["installation_place"] = installation_place
    if type: params["type"] = type
    if is_active: params["is_active"] = is_active
    if client_sector: params["client_sector"] = client_sector
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    if node_id: params["node_id"] = node_id
    if reading_date: params["reading_date"] = reading_date
    if report: params["report"] = report
    if columns: params["columns"] = columns
    return json.dumps(api_get("/api/v1/meter/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def meter_read(id: int) -> str:
    """Получить детальную информацию об измерителе (счётчике) по ID."""
    return json.dumps(api_get(f"/api/v1/meter/{id}/"), ensure_ascii=False, indent=2)


@mcp.tool()
def meter_model_list(
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список типов (моделей) измерителей."""
    params = {}
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/meter/model/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def meter_model_read(id: int) -> str:
    """Получить тип (модель) измерителя по ID."""
    return json.dumps(api_get(f"/api/v1/meter/model/{id}/"), ensure_ascii=False, indent=2)


@mcp.tool()
def meter_commands(id: int) -> str:
    """Получить последнее показание и дату последнего сообщения измерителя."""
    return json.dumps(api_get(f"/api/v1/meter/{id}/commands/"), ensure_ascii=False, indent=2)


@mcp.tool()
def meter_valve(id: int) -> str:
    """Проверить, поддерживает ли измеритель управление клапаном."""
    return json.dumps(api_get(f"/api/v1/meter/{id}/valve/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  METER INSTALLATION — Монтаж измерителей
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def meter_installation_list(
    meters__isnull: str = "",
    device__node_service_company: str = "",
    resource_type: str = "",
    type: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список монтажей измерителей."""
    params = {}
    if meters__isnull: params["meters__isnull"] = meters__isnull
    if device__node_service_company: params["device__node_service_company"] = device__node_service_company
    if resource_type: params["resource_type"] = resource_type
    if type: params["type"] = type
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/meter_installation/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def meter_installation_read(id: int) -> str:
    """Получить монтаж измерителя по ID."""
    return json.dumps(api_get(f"/api/v1/meter_installation/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  NETWORK SERVERS — Сетевые серверы
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def network_server_list(
    ordering: str = "",
    type__trans_tech_type: str = "",
    type__trans_tech_type__name: str = "",
    type__trans_tech_type__name__icontains: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список сетевых серверов. Фильтры по типу технологии передачи."""
    params = {}
    if ordering: params["ordering"] = ordering
    if type__trans_tech_type: params["type__trans_tech_type"] = type__trans_tech_type
    if type__trans_tech_type__name: params["type__trans_tech_type__name"] = type__trans_tech_type__name
    if type__trans_tech_type__name__icontains: params["type__trans_tech_type__name__icontains"] = type__trans_tech_type__name__icontains
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/network_server/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def network_server_read(id: int) -> str:
    """Получить сетевой сервер по ID."""
    return json.dumps(api_get(f"/api/v1/network_server/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  NODES — Узлы (иерархия)
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def node_list(
    ordering: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
    parent: str = "",
) -> str:
    """Получить список узлов (иерархия организаций/объектов).
    parent: Передайте 'none' для получения рекурсивного дерева корневых узлов с количеством измерителей.
    """
    params = {}
    if ordering: params["ordering"] = ordering
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    if parent: params["parent"] = parent
    return json.dumps(api_get("/api/v1/node/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def node_read(id: int) -> str:
    """Получить узел по ID."""
    return json.dumps(api_get(f"/api/v1/node/{id}/"), ensure_ascii=False, indent=2)


@mcp.tool()
def node_type_list(
    ordering: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список типов узлов."""
    params = {}
    if ordering: params["ordering"] = ordering
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/node/type/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def node_type_read(id: int) -> str:
    """Получить тип узла по ID."""
    return json.dumps(api_get(f"/api/v1/node/type/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  DASHBOARD — Дашборд
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def dashboard_active_meters(
    node_id: int = 0,
    days: int = 0,
) -> str:
    """Получить график активных счётчиков за период.
    node_id: ID узла для фильтрации.
    days: Глубина графика в днях (1-90, по умолчанию 30).
    """
    params = {}
    if node_id: params["node_id"] = node_id
    if days: params["days"] = days
    return json.dumps(api_get("/api/v1/node/dashboard/active_meters/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def dashboard_resource_type_stats(
    node_id: int = 0,
) -> str:
    """Получить статистику по типам ресурсов (вода, газ, электричество и т.д.).
    node_id: ID узла для фильтрации.
    """
    params = {}
    if node_id: params["node_id"] = node_id
    return json.dumps(api_get("/api/v1/node/dashboard/resource_type_stats/", params), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  OBJECT TYPES — Типы объектов
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def object_type_list(
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список типов объектов."""
    params = {}
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/object_type/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def object_type_read(id: int) -> str:
    """Получить тип объекта по ID."""
    return json.dumps(api_get(f"/api/v1/object_type/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  READING CORRECTIONS — Корректировки показаний
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def reading_correction_list(
    dt__gte: str = "",
    dt__lte: str = "",
    meter: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список корректировок показаний. Фильтры: дата, измеритель."""
    params = {}
    if dt__gte: params["dt__gte"] = dt__gte
    if dt__lte: params["dt__lte"] = dt__lte
    if meter: params["meter"] = meter
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/reading_correction/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def reading_correction_read(id: int) -> str:
    """Получить корректировку показания по ID."""
    return json.dumps(api_get(f"/api/v1/reading_correction/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  RESOURCE TYPES — Типы ресурсов
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def resource_type_list(
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список типов ресурсов (вода, газ, электричество, тепло)."""
    params = {}
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/resource_type/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def resource_type_read(id: int) -> str:
    """Получить тип ресурса по ID."""
    return json.dumps(api_get(f"/api/v1/resource_type/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  SERVICE COMPANIES — Сервисные компании
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def service_company_list(
    ordering: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список сервисных компаний."""
    params = {}
    if ordering: params["ordering"] = ordering
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/service_company/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def service_company_read(id: int) -> str:
    """Получить сервисную компанию по ID."""
    return json.dumps(api_get(f"/api/v1/service_company/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  SUPPLIER COMPANIES — Поставщики ресурсов
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def supp_company_list(
    ordering: str = "",
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список поставщиков ресурсов."""
    params = {}
    if ordering: params["ordering"] = ordering
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/supp_company/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def supp_company_read(id: int) -> str:
    """Получить поставщика ресурсов по ID."""
    return json.dumps(api_get(f"/api/v1/supp_company/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  USERS — Пользователи
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def user_list(
    search: str = "",
    page: int = 0,
    page_size: int = 0,
) -> str:
    """Получить список пользователей системы."""
    params = {}
    if search: params["search"] = search
    if page: params["page"] = page
    if page_size: params["page_size"] = page_size
    return json.dumps(api_get("/api/v1/user/", params), ensure_ascii=False, indent=2)


@mcp.tool()
def user_read(id: int) -> str:
    """Получить пользователя по ID."""
    return json.dumps(api_get(f"/api/v1/user/{id}/"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
