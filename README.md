Гидроксид алюминия
==================

Моделирование отбора заказов и производства 4 продуктов на основе
гидроксида алюминия.

-   [Описание производства и сбыта](#tech)
-   [Допущения модели](#assumptions)
-   [Текущий этап работ](#leg)

<a id="tech"></a>

## 1. Описание производства и сбыта


#### Продукты и технологическая последовательность

Завод выпускает четыре продукта, которые мы можем обозначим буквами `A`,
`B`, `C`, `D`:

-   `A`: продукт марки H
-   `B`: продукт марки H10
-   `C`: продукт марки TA-HSA-10
-   `D`: продукт марки TA-240

Исходным сырьем для всех продуктов является гироксид алюминия. Из него
делаются порошки марки H и TA-240. Продукты марок H10 и TA-HSA-10
являются результатом последовательной механической и термической
обработки продукта марки H.

Последовательность производства показана на схеме ниже:

      Al(OH)3 --> H --> H10 --> TA-HSA-10
      Al(OH)3 --> TA-240

      сырье -> A -> B -> C
      сырье -> D

Завод продает продукты всех четырех марок `A`, `B`, `C`, `D`.

#### Характеристики производства

-   Мощности производства по продуктам ограничены значениями тонн в день
    (`max_capacity`).

-   Затраты производства описываются константой переменных затрат по
    каждом продукту, долл за тонну (`unit_cost`).

-   Известны потребности в продукте X, чтобы выпустить одну тонну
    продукта Y ([inputs_material.py](inputs_material.py)).

-   Продукт может храниться на складе ограниченное время (набирает
    влагу). Срок хранения задан для каждого продукта в днях
    (`max_storage_days`).

Названия переменных даны для файла [inputs.py](inputs.py).

#### Сбыт

-   Завод обычно получает больше заказов, чем может выпустить, стоит
    задача как выбрать нужные заказы и как организовать производство с
    учетом хранения.
-   Нам известны индикативные (средние) цены на продукты
    (`expected_price`).
-   Заявка принимается в формате
    `(продукт, цена, день поставки, количество)`
-   Каждая покупателя заявка либо принимается, либо отклоняется.

<a id="assumptions"></a>

## 2. Допущения модели

Для решения текущей задачи приняты следующие допущения:

-   Производство дискретно по дням
-   Cрок производства от загрузки продукта-предшественника до получения
    продукта составляет 1 день
-   Указанный срок хранения - это срок хранения продукта на складе, а не
    весь срок жизни продукта
-   Все заказы на месяц известны в начале месяца
-   В начале и в конце месяца нулевые остатки продукции на складе
-   Нет ограничений по емкости склада
-   Стоимость хранения на складе может вводится экспертно
-   Нет неучтенных затрат производства (например, пуск оборудования)
-   Нет предпочтений по клиентам завода, заявки на покупку не связаны
    друг с другом
-   Нет ремонтов и поломок оборудования

В ходе работы исполнителем могут вводиться новые допущения, отражающие
необходимые решения в формулировке и упрощении задачи.

<a id="leg"></a>

## 3. Текущий этап работ

#### Задачи этапа

Для первого этапа работ мы решаем наиболее простую, демонстрационную
задачу отбора заявок на покупку и планирования производства в рамках
принятых допущений, указанных выше.

Решение этой задачи может не совпадать с принятой бизнес-практикой
планирования сбыта и производства на заводе, учитывающие большее число
характеристик и свойств производства и критериев оценки качества
решения.

Для решения задачи, наиболее близкой к фактической работе завода
("конечная задача"), может потребоваться изменение предложенных на
данном этапе методологии расчетов и способов анализа и представления
результатов.

В случае роста сложности конечной задачи, решаемой за пределами данного
этапа, может потребоваться использование быстродействующих коммерческих
пакетов (солверов) для решения задач линейного программирования (CPLEX,
Gurobi или других).

#### Результаты этапа

1.  Представлен код для генерации условного портфеля заказов по 4
    продуктам на месяц, с объемом спроса, превышающий возможный объем
    производства.

2.  Представлен код (python) для решения задачи линейного
    программирования, который по следующим характеристикам производства
    четырех продуктов:

    -   ограничение мощности производства по продуктам
    -   материальные потребности (расходы) между продуктами
    -   максимальный срок хранения продукта на складе
    -   константы переменной стоимости производства

    и списку заказов на начало месяца в формате `(продукт, цена, день поставки, количество)`

    выдает список выбранных заказов и график производства по продуктам и
    дням в течение месяца, отвечающий требованию получить максимальную
    прибыль предприятия исходя из принятых допущений о его работе.

3.  Даны комментарии по работе алгоритма и принятым решениям при его
    создании и настройке, определены возможные пути доработки алгоритма.


#### План реализации

Ход решения (может меняться исполнителем):

-   [ ] генерация условного портфеля заказов из 1 продукта на 7 дней
-   [ ] определение фотрмата результатов (выбранные заказы, план
    производства)
-   [ ] производство 1 товара за неделю, с ограничениями хранения
-   [ ] генерация условного портфеля заказов из 4 продуктов на 7 дней
-   [ ] производство 4 несвязанных товаров за неделю
-   [ ] расширение размерности до 1 месяца
-   [ ] связанное производство (один из товаров - сырье для другого)

В течение всех работ (может меняться исполнителем):

-   [ ] документирование принятых решений в разработке алгоритма
-   [ ] другие работы, рефакторинг кода
