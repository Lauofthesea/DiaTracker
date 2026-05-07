"""
Quick script to run migration 008 - Add meal_predictions table
"""
import os
import sys
from sqlalchemy import create_engine, text

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings

def run_migration():
    """Run the migration to create meal_predictions table"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.connect() as conn:
        # Check if table already exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'meal_predictions'
            );
        """))
        exists = result.scalar()
        
        if exists:
            print("✅ meal_predictions table already exists!")
            return
        
        print("Creating meal_predictions table...")
        
        # Create the table
        conn.execute(text("""
            CREATE TABLE meal_predictions (
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
        """))
        
        # Create indexes
        conn.execute(text("CREATE INDEX ix_meal_predictions_user_id ON meal_predictions(user_id);"))
        conn.execute(text("CREATE INDEX ix_meal_predictions_predicted_at ON meal_predictions(predicted_at);"))
        conn.execute(text("CREATE INDEX ix_meal_predictions_risk_level ON meal_predictions(risk_level);"))
        
        conn.commit()
        
        print("✅ meal_predictions table created successfully!")
        print("✅ Indexes created successfully!")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
