ALTER USER 'root'@'localhost' IDENTIFIED BY 'Parthsam@5';

GRANT ALL PRIVILEGES ON attendance_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

-- attendance_db.sql
create database attendance;
USE attendance;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    gender ENUM('M', 'F') NOT NULL
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    attendance_date DATE,
    status ENUM('Present', 'Absent'),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

select * from attendance;
select * from students;
SELECT 
    students.student_id,
    students.student_name,
    attendance.attendance_date,
    attendance.status
FROM 
    students
JOIN 
    attendance 
ON 
    students.student_id = attendance.student_id;
    
    -- for Boys
    SELECT status, COUNT(*) 
FROM attendance 
JOIN students ON attendance.student_id = students.student_id 
WHERE attendance_date = '2024-10-28' AND students.gender = 'M'
GROUP BY status;

-- for Girls
SELECT status, COUNT(*) 
FROM attendance 
JOIN students ON attendance.student_id = students.student_id 
WHERE attendance_date = '2024-10-28' AND students.gender = 'F'
GROUP BY status;
