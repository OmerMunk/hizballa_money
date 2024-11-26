# מערכת מודיעין פיננסי - Finance Intelligence System
## פרויקט סיום קורס Data Engineering

### מבוא
מערכת זו פותחה עבור יחידת הסייבר של המוסד לצורך זיהוי וניטור דפוסי הלבנת הון של חיזבאללה. המערכת משלבת מספר טכנולוגיות מפתח:
- Neo4j לניתוח קשרים וגרפים
- Redis לשמירת נתונים בזיכרון וחישוב בזמן אמת
- Flask ליצירת שירותי REST
- Pandas לניתוח נתונים
- Docker לקונטיינריזציה

### דרישות מקדימות
- Python
- Docker & Docker Compose
- Postman
- Git

### הוראות התקנה
1. שכפול המאגר:
```bash
git clone https://github.com/OmerMunk/hizballa_money.git
cd hizballa_money
```

2. יצירת סביבת Python:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# או
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. הרצת המערכת:
```bash
docker-compose up -d
```

### מבנה המערכת
המערכת מורכבת משלושה שירותים עיקריים:

1. **Transaction Service** (port 5001)
   - קליטת העברות כספים
   - שמירת נתונים ב-Neo4j
   - חיפוש וסינון העברות

2. **Analysis Service** (port 5002)
   - זיהוי דפוסים חשודים
   - ניתוח רשתות העברות
   - יצירת ויזואליזציות

3. **Scoring Service** (port 5003)
   - חישוב ציוני סיכון
   - ניהול רשימות שחורות
   - מדדי סיכון מצטברים

### משימות הפרויקט

#### שלב 1: הכנה והתקנה (שעה)
- [ ] התקנת כל הדרישות המקדימות
- [ ] הרצת המערכת
- [ ] וידוא תקינות באמצעות Healthcheck
- [ ] ייבוא קובץ Postman

#### שלב 2: מידול נתונים (שעתיים)
- [ ] תכנון מודל הגרף ב-Neo4j
- [ ] הגדרת אינדקסים
- [ ] תכנון מבני נתונים ב-Redis
- [ ] יצירת שאילתות Cypher בסיסיות

#### שלב 3: פיתוח לוגיקה (שעתיים)
- [ ] מימוש אלגוריתם זיהוי מעגלים
- [ ] פיתוח מודל ציוני סיכון
- [ ] יצירת ויזואליזציות
- [ ] כתיבת בדיקות

#### שלב 4: אינטגרציה ובדיקות (שעה)
- [ ] בדיקות End-to-End
- [ ] טיפול במקרי קצה
- [ ] אופטימיזציה
- [ ] תיעוד

### API Endpoints

#### Transaction Service
```
POST /api/v1/transactions
GET /api/v1/transactions/{id}
GET /api/v1/transactions/search
```

#### Analysis Service
```
GET /api/v1/analysis/patterns
GET /api/v1/analysis/metrics
GET /api/v1/analysis/visualization
```

#### Scoring Service
```
GET /api/v1/risk-score/{entity_id}
POST /api/v1/blacklist
GET /api/v1/risk-metrics
```