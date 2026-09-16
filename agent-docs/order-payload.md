# Что парсер отправляет в бэкенд и что бэкенд с этим делает

## Сборка payload (`src/utils/format_order_data.py`)
Один Etsy receipt → `OrderData{order, client, city, order_items}`; пачка по магазину →
`UploadingOrderData{shop_id, is_full_data_updating, orders_data}` → `POST /parser/orders/upload/`
(заголовок `Authorization: Bearer <API_AUTH_TOKEN>` — токен сервисного пользователя парсера в CMS).

| Поле | Откуда | Заметки |
|---|---|---|
| `order.order_id` | `receipt_id` строкой | Номер заказа Etsy; в CMS это `order.order_id`, уникален в паре с `shop_id` |
| `order.status` | `receipt.status` | `Paid`, `Completed`, `Canceled`, `Fully Refunded`… как отдаёт Etsy |
| `order.date` | `f"{day}.{month}.{year}"` | **Без ведущих нулей**: `3.9.2025`. В БД хранится строкой |
| `order.quantity` | сумма `quantity` по всем позициям | Штук в заказе, не строк |
| `order.buyer_paid`, `order.tax` | `grandtotal`, `total_tax_cost` | Из центов в доллары через `divisor` |
| `order.receipt_shipping_id`, `tracking_code` | `shipments[0]` | Пустые строки, если отправки нет. **Стоимости доставки в payload нет** |
| `client` | `buyer_user_id`, `name`, `buyer_email` | Собирается в `try/except: pass` — при сбое все поля `None` |
| `city` | `city`, `state`, `country_iso` | То же |
| `order_items[].uniquename` | `transaction.sku` | Полный SKU из листинга, включая часть после `#` |
| `order_items[].quantity`, `amount` | цена × кол-во − купон | |
| `order_items[].engraving_info` | JSON вариаций `{name: value}` + `listing_id`, `product_id`, `transaction_type` | То, что видит гравёр (шрифт, персонализация и т.д.) |

Ключ товара — SKU. До `#` — складская часть (`PN CH-PN CG-DCSB`: сегменты через `-`,
`.N` — количество в сегменте), после `#` — информация для гравёра. Подробнее про формат SKU —
`backend/agent-docs/business-rules.md`.

## Обработка на бэкенде (`backend/src/models/system/parser_model.py::upload_orders`)
Эндпоинт отвечает 200 сразу, обработка идёт в `BackgroundTasks`. По каждому заказу:
1. город/штат/страна создаются при отсутствии;
2. заказ ищется по `(shop_id, order_id)`;
3. **заказ есть** → обновляются только статус, `receipt_shipping_id`, `tracking_code`.
   При переходе в `Completed` — списание со склада (`storage_off`) по каждой строке заказа,
   в строку пишется себестоимость. При `is_full_data_updating` дополнительно обновляются
   клиент и город (используется `parser_all.py`);
4. **заказа нет** → создаётся товар (`good`) по SKU, если его нет (и связи со складскими
   позициями по сегментам SKU), считаются `shipping` (константа по количеству), `full_fee`
   и `profit` (формулы из таблицы `fees_and_expenses` магазина), создаётся заказ со строками,
   и только после успешной вставки — списание со склада, если заказ уже `Completed`.
   Конфликт по уникальному индексу (параллельная загрузка того же заказа) не роняет задачу:
   откат, повторное чтение, ветка обновления.

Следствия для парсера:
- повторная отправка уже загруженных заказов безопасна и ожидаема (см. окно в
  [parser-loop.md](parser-loop.md));
- ошибка в SKU на Etsy = «мусорный» товар в CMS (`Automatically created by storage_off
  function`), парсер это не фильтрует;
- поля после `#` уезжают в `engraving_info`/`description` товара и не должны терять регистр
  и апострофы — клиент читает их как есть.
