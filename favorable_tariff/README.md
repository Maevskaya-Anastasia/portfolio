# Определение выгодного тарифа

***

**Заказчик** — мобильный оператор.

**Задача** — построить систему, способную проанализировать поведение клиентов.

**Цель** — предложить пользователям новый тариф, так как многие клиенты пользуются архивными тарифами.

***

**Данные** о поведении клиентов, которые уже перешли на эти тарифы.
- `сalls` — количество звонков,
- `minutes` — суммарная длительность звонков в минутах,
- `messages` — количество sms-сообщений,
- `mb_used` — израсходованный интернет-трафик в Мб,
- `is_ultra` — каким тарифом пользовался в течение месяца («Ультра» — 1, «Смарт» — 0).

***

**План работы**
1. Подготовить данные.
1. Провести работу с моделями