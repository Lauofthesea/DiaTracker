-- Create meal_predictions table for RF #1 glucose predictions

CREATE TABLE IF NOT EXISTS meal_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    food_entry_id UUID REFERENCES food_entries(entry_id) ON DELETE SET NULL,
    fasting_glucose FLOAT NOT NULL,
    available_carbs_g FLOAT NOT NULL,
    fat_g FLOAT NOT NULL,
    protein_g FLOAT NOT NULL,
    fiber_g FLOAT NOT NULL,
    bmi FLOAT NOT NULL,
    age INTEGER NOT NULL,
    gender INTEGER NOT NULL,
    predicted_glucose_1hr FLOAT NOT NULL,
    confidence_lower FLOAT,
    confidence_upper FLOAT,
    risk_level VARCHAR(10) NOT NULL CHECK (risk_level IN ('Low', 'Mid', 'High')),
    model_version VARCHAR(50) NOT NULL,
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS ix_meal_predictions_user_id ON meal_predictions(user_id);
CREATE INDEX IF NOT EXISTS ix_meal_predictions_predicted_at ON meal_predictions(predicted_at);
CREATE INDEX IF NOT EXISTS ix_meal_predictions_risk_level ON meal_predictions(risk_level);

-- Verify table was created
SELECT 'meal_predictions table created successfully!' AS status;
