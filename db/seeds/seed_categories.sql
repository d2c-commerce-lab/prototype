INSERT INTO categories (category_id, category_name, category_depth, category_status, created_at, updated_at)
VALUES
  (gen_random_uuid(), 'Desk Setup', 1, 'active', NOW(), NOW()),
  (gen_random_uuid(), 'Productivity Tools', 1, 'active', NOW(), NOW()),
  (gen_random_uuid(), 'Office Accessories', 1, 'active', NOW(), NOW());