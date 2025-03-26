-- find the class name and country for all classes with at least 10 guns
SELECT class, country
FROM classes
WHERE numGuns >= 10;


-- find the name of all ships launched prior to 1918, but call the resulting column shipName
SELECT name AS shipName
FROM ships
WHERE launched < 1918;


-- find the names of ships sunk in battle and the names of the battle in which they were sunk
SELECT
    ship AS shipName,
    battle
FROM outcomes
WHERE result = 'sunk';


-- find all ships that have the same name as their class
-- (careful! use class instead of 'class', otherwise you will compare it to the string 'class')
SELECT name
FROM ships
WHERE name = class;


-- find the names of all ships that being with the letter "R"
SELECT name
FROM ships
WHERE name LIKE 'R%';


-- find the ships heavier tha 35000 tons
SELECT s.name
FROM
    ships s,
    classes c
WHERE s.class = c.class
AND c.displacement > 35000;


-- list the name, displacement, and number of guns of the ships engaged in the battle of Guadalcanal
SELECT
    s.name,
    c.displacement
    c.numGuns
FROM
    ships s,
    outcomes o,
    classes c
WHERE s.name = o.ship
    AND s.class = c.class
    AND o.battle = 'Guadalcanal';


-- list all the ships mentioned in the database (remember that allt hese ships may not appear in the ships relation)
SELECT name AS shipName FROM ships
UNION
SELECT ship AS shipName FROM outcomes;


-- find those countries that had both battleships and battlecruisers
-- (solution 1: no INTERSECT)
SELECT c1.country
FROM
    classes c1,
    classes c2
WHERE c1.country = c2.country
    AND c1.type = 'bb' AND c2.type = 'bc';

-- (solution 2: using INTERSECT)
-- WARNING: this solution is not valid in MySQL since it does not have the INTERSECT operator;
--          it is however valid in SQLite as it supports INTERSECT
SELECT country FROM classes WHERE type = 'bb'
INTERSECT
SELECT country FROM classes WHERE type = 'bc';


-- find those ships that were damaged in one battle but later fought in another
-- (solution 1: using a view; note that there are 2 queries -- one for the view, the other for the SELECT)
CREATE VIEW damagedShips AS
SELECT 
    ship AS name, 
    date AS damagedate
FROM 
    battles, 
    outcomes
WHERE battles.name = outcomes.battle
    AND outcomes.result = 'damaged';

SELECT damagedShips.name
FROM damagedShips, battles, outcomes
WHERE damagedShips.name = outcomes.ship
    AND battles.name = outcomes.battle
    AND battles.date > damagedShips.damagedate;

-- (solution 2: using a subquery)
SELECT damagedShips.name
FROM (SELECT 
        ship AS name,
        date AS damagedate
    FROM
        battles,
        outcomes
    WHERE battles.name = outcomes.battle
        AND outcomes.result = 'damaged') AS damagedShips,
    battles,
    outcomes
WHERE damagedShips.name = outcomes.ship
    AND battles.name = outcomes.battle
    AND battles.date > damagedShips.damagedate;


-- find those battles with at least three ships of the same country
-- (solution 1: using aggregate functions)
SELECT o.battle
FROM
    outcomes o,
    ships s,
    classes c
WHERE o.ship = s.name
    AND s.class = c.class
    GROUP BY c.country, o.battle
    HAVING COUNT(o.ship) > 3;

-- (solution 2: without using aggregate functions -- subqueries)
SELECT *
FROM
    (
        SELECT 
            Outcomes.ship, 
            Classes.country, 
            Outcomes.battle
        FROM 
            Outcomes,
            Ships, 
            Classes
        WHERE Outcomes.ship = Ships.name 
            AND Ships.class = Classes.class
    ) t1,
    (
        SELECT 
            Outcomes.ship, 
            Classes.country, 
            Outcomes.battle
        FROM 
            Outcomes,
            Ships, 
            Classes
        WHERE Outcomes.ship = Ships.name AND Ships.class = Classes.class
    ) t2,
    (
        SELECT 
            Outcomes.ship, 
            Classes.country, 
            Outcomes.battle
        FROM 
            Outcomes,
            Ships, 
            Classes
        WHERE Outcomes.ship = Ships.name 
            AND Ships.class = Classes.class
    ) t3
WHERE t1.country = t2.country 
    AND t1.country = t3.country 
    AND t2.country = t3.country
    AND t1.ship <> t2.ship
    AND t1.ship <> t3.ship 
    AND t3.ship <> t2.ship 
    AND t1.battle = t2.battle 
    AND t1.battle = t3.battle 
    AND t2.battle = t3.battle;