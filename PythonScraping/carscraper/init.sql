CREATE TABLE IF NOT EXISTS car_products (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,           -- Унікальний URL
    title TEXT,                         -- Назва автомобіля
    price_usd INTEGER,                  -- Ціна в $ (число)
    odometer INTEGER,                   -- Пробіг в км (95000)
    username TEXT,                      -- Ім'я продавця
    phone_number BIGINT[],              -- Телефон (38063......)
    image_url TEXT[],                   -- URL зображення
    image_count INTEGER,                -- Кількість фото
    car_number TEXT,                    -- Номерний знак
    car_vin TEXT,                       -- VIN код
    datetime_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);