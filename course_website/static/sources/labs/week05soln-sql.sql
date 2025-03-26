-- part 1: views

-- create a view called Calgary_Employees of all employees whose city is Calgary
CREATE VIEW Calgary_Employees
AS
SELECT * FROM employees
WHERE city = 'Calgary';

-- create a view called Managers of all employees who are some sort of manager
CREATE VIEW Managers
AS
SELECT * FROM employees
WHERE title LIKE '%Manager%';

-- create a view called Small_Employee that is the same as the Employee table but only contains the following columns
CREATE VIEW Small_Employee
AS
SELECT
    EmployeeId,
    FirstName,
    LastName,
    Title,
    Phone,
    Email
FROM employees;

------------------------------------------------------

-- part 2: GROUP BY

-- return the result set containing the album ID and number of tracks per album for every album ID in the relation
SELECT
    albumid,
    COUNT(trackid)
FROM
    tracks
GROUP BY
    albumid;

-- do the same as above but order the groups in descending order
SELECT
    albumid,
    COUNT(trackid)
FROM
    tracks
GROUP BY
    albumid
ORDER BY COUNT(trackid) DESC;

-- do the same as above but include the album title as well
SELECT
    tracks.albumid,
    title,
    COUNT(trackid)
FROM
    tracks
INNER JOIN albums ON albums.albumid = tracks.albumid
GROUP BY
    tracks.albumid;

-- do the same as above but only return records where trackid > 15
SELECT
    tracks.albumid,
    title,
    COUNT(trackid)
FROM
    tracks
INNER JOIN albums ON albums.albumid = tracks.albumid
GROUP BY
    tracks.albumid
HAVING COUNT(trackid) > 15;