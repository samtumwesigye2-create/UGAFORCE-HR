-- Ensure the authenticated primary HR administrator is also represented in the workforce.
-- This makes the first administrator eligible to act as hiring manager immediately.
WITH admins AS (
    SELECT u.id AS user_id,
           u.username,
           'HR-ADMIN-' || upper(substr(replace(u.id::text, '-', ''), 1, 8)) AS employee_number,
           r.id AS role_id
    FROM ugaforce_hr_users u
    JOIN ugaforce_hr_roles r ON r.name = 'HR_ADMIN'
    WHERE u.role_name = 'HR_ADMIN'
      AND u.active = true
      AND u.employee_id IS NULL
), inserted AS (
    INSERT INTO ugaforce_hr_employees(
        employee_number, first_name, last_name, work_email, hire_date,
        employment_status, job_title, role_id, employment_type, pay_currency
    )
    SELECT a.employee_number,
           'Primary',
           'Administrator',
           CASE WHEN position('@' in a.username) > 0 THEN lower(a.username) ELSE NULL END,
           current_date,
           'active',
           'HR Administrator',
           a.role_id,
           'full_time',
           'USD'
    FROM admins a
    ON CONFLICT (employee_number) DO NOTHING
    RETURNING id, employee_number
)
UPDATE ugaforce_hr_users u
SET employee_id = e.id,
    updated_at = now()
FROM ugaforce_hr_employees e
WHERE u.role_name = 'HR_ADMIN'
  AND u.active = true
  AND u.employee_id IS NULL
  AND e.employee_number = 'HR-ADMIN-' || upper(substr(replace(u.id::text, '-', ''), 1, 8));
