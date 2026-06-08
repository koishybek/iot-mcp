# Smart Metrix MCP Server

MCP-сервер для IoT-платформы **Smart Metrix** (`sm.iot-exp.kz`).  
Предоставляет **49 GET-тулов** для чтения данных системы учёта ресурсов через MCP-протокол.

## 🚀 Деплой на FastMCP Cloud

### 1. Залить в GitHub
```bash
git init
git add .
git commit -m "Smart Metrix MCP Server"
git remote add origin https://github.com/YOUR_USER/smart-metrix-mcp.git
git push -u origin main
```

### 2. Развернуть на FastMCP Cloud
1. Зайти на [fastmcp.app](https://fastmcp.app)
2. Залогиниться через GitHub
3. Выбрать репозиторий `smart-metrix-mcp`
4. Получить URL: `https://xxx.fastmcp.app/mcp`

### 3. Подключить к Claude / ChatGPT
Вставить полученный URL в настройки MCP-коннекторов.

---

## 📁 Структура проекта

| Файл               | Описание                                           |
|---------------------|-----------------------------------------------------|
| `server.py`         | **Основной** — Python MCP-сервер (FastMCP) для деплоя |
| `index.js`          | Node.js MCP-сервер (для локального использования)    |
| `openapi`           | Swagger 2.0 спецификация API Smart Metrix           |
| `requirements.txt`  | Python-зависимости                                   |
| `package.json`      | Node.js-зависимости                                  |

---

## 🔧 Локальный запуск

### Python (FastMCP)
```bash
pip install -r requirements.txt
python server.py
# Сервер будет доступен по http://localhost:8000/mcp
```

### Node.js (stdio)
```bash
npm install
node index.js
```

---

## 🛠 Доступные тулы (49)

### Адреса
- `address_list` — Список адресов
- `address_read` — Адрес по ID

### Хранилище данных
- `data_store_list` — Обработанные данные (meter_id, период, даты)
- `data_store_read` — Запись по ID
- `data_store_default_list` — Сырые (необработанные) данные

### Устройства
- `device_list` — Список устройств
- `device_read` — Устройство по ID
- `device_mode_list` — Режимы устройств
- `device_mode_read` — Режим по ID
- `device_model_list` — Модели устройств
- `device_model_read` — Модель по ID

### Скачивание
- `downloads_read` — Статус файла по task_id

### События
- `event_list` — Список событий
- `event_type_list` — Типы событий
- `event_type_read` — Тип события по ID

### Шлюзы
- `gateway_list` — Список шлюзов
- `gateway_read` — Шлюз по ID
- `gateway_stats` — Статистика шлюза

### Места установки
- `installation_place_list` / `installation_place_read`

### Геолокация
- `location_list` — Местоположение счётчиков на карте

### Измерители (счётчики)
- `meter_list` — Список измерителей (мощные фильтры)
- `meter_read` — Измеритель по ID
- `meter_model_list` / `meter_model_read` — Типы измерителей
- `meter_commands` — Последнее показание и дата
- `meter_valve` — Поддержка клапана

### Монтаж
- `meter_installation_list` / `meter_installation_read`

### Сетевые серверы
- `network_server_list` / `network_server_read`

### Узлы (иерархия)
- `node_list` — Список узлов (дерево при parent='none')
- `node_read` — Узел по ID
- `node_type_list` / `node_type_read`

### Дашборд
- `dashboard_active_meters` — График активных счётчиков
- `dashboard_resource_type_stats` — Статистика по ресурсам

### Справочники
- `object_type_list` / `object_type_read` — Типы объектов
- `resource_type_list` / `resource_type_read` — Типы ресурсов
- `reading_correction_list` / `reading_correction_read` — Корректировки

### Компании
- `service_company_list` / `service_company_read`
- `supp_company_list` / `supp_company_read`

### Пользователи
- `user_list` / `user_read`
