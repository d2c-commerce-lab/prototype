INSERT INTO campaigns (
    campaign_id,
    campaign_name,
    campaign_type,
    campaign_status,
    start_at,
    end_at,
    budget_amount,
    created_at,
    updated_at
) VALUES
('22222222-2222-2222-2222-222222222001', 'Spring Desk Refresh', 'seasonal', 'active', '2026-04-01 00:00:00', '2026-05-31 23:59:59', 3000000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('22222222-2222-2222-2222-222222222002', 'New User Welcome Campaign', 'signup_promo', 'active', '2026-01-01 00:00:00', '2026-12-31 23:59:59', 1500000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('22222222-2222-2222-2222-222222222003', 'Focus Week Promotion', 'thematic', 'ended', '2026-03-01 00:00:00', '2026-03-15 23:59:59', 1000000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('22222222-2222-2222-2222-222222222004', 'Cart Recovery Campaign', 'retargeting', 'planned', '2026-06-01 00:00:00', '2026-06-30 23:59:59', 2000000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (campaign_id) DO NOTHING;
