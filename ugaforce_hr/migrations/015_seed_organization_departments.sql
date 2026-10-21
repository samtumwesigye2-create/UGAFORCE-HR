-- Seed a usable corporate organization so Recruiting and People are not blocked by an empty department table.
-- Idempotent by case-insensitive department name; existing user-created departments are preserved.

CREATE UNIQUE INDEX IF NOT EXISTS uq_ugaforce_hr_departments_name_ci
ON ugaforce_hr_departments (lower(name));

INSERT INTO ugaforce_hr_departments(name)
SELECT v.name
FROM (VALUES
  ('Executive Department'),
  ('Human Resources'),
  ('Finance'),
  ('Operations'),
  ('Technology & Systems'),
  ('Procurement & Supply Chain'),
  ('Engineering'),
  ('Security & Risk'),
  ('Legal & Compliance'),
  ('Strategy & Analytics'),
  ('Communications'),
  ('Administration')
) AS v(name)
WHERE NOT EXISTS (
  SELECT 1 FROM ugaforce_hr_departments d WHERE lower(d.name)=lower(v.name)
);

WITH structure(parent_name, child_name) AS (VALUES
  ('Executive Department','Executive Office'),
  ('Executive Department','Corporate Governance'),
  ('Human Resources','Talent Acquisition'),
  ('Human Resources','People Operations'),
  ('Human Resources','Learning & Development'),
  ('Finance','Accounting'),
  ('Finance','Treasury'),
  ('Finance','Payroll'),
  ('Operations','Network Operations'),
  ('Operations','Field Operations'),
  ('Operations','Service Delivery'),
  ('Technology & Systems','Platform Engineering'),
  ('Technology & Systems','IT Infrastructure'),
  ('Technology & Systems','Enterprise Applications'),
  ('Procurement & Supply Chain','Purchasing'),
  ('Procurement & Supply Chain','Supplier Management'),
  ('Procurement & Supply Chain','Logistics & Warehousing'),
  ('Engineering','Systems Engineering'),
  ('Engineering','Product Engineering'),
  ('Engineering','Quality Assurance'),
  ('Security & Risk','Physical Security'),
  ('Security & Risk','Risk Management'),
  ('Security & Risk','Security Operations'),
  ('Legal & Compliance','Legal Affairs'),
  ('Legal & Compliance','Compliance & Ethics'),
  ('Strategy & Analytics','Business Intelligence'),
  ('Strategy & Analytics','Planning & Performance'),
  ('Communications','Public Affairs'),
  ('Communications','Internal Communications'),
  ('Administration','Facilities'),
  ('Administration','Fleet & General Services')
)
INSERT INTO ugaforce_hr_departments(name,parent_dept_id)
SELECT s.child_name,p.id
FROM structure s
JOIN ugaforce_hr_departments p ON lower(p.name)=lower(s.parent_name)
WHERE NOT EXISTS (
  SELECT 1 FROM ugaforce_hr_departments d WHERE lower(d.name)=lower(s.child_name)
);
