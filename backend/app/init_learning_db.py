import os
import sys

# Add backend directory to sys.path to import mysql_storage
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mysql_storage import mysql_storage

def init_learning_db():
    print("Initializing learning database tables...")
    conn = mysql_storage.get_connection()
    if not conn:
        print("Failed to connect to database.")
        return

    try:
        with conn.cursor() as cursor:
            # 1. Create categories table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_name (name)
            )
            """)

            # 2. Create days table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS days (
                id INT AUTO_INCREMENT PRIMARY KEY,
                day_number INT NOT NULL COMMENT '第几天',
                week_number INT NOT NULL COMMENT '第几周',
                title VARCHAR(200) COMMENT '天标题',
                description TEXT COMMENT '描述',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY idx_week_day (week_number, day_number)
            )
            """)

            # 3. Create words table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INT AUTO_INCREMENT PRIMARY KEY,
                word VARCHAR(100) NOT NULL,
                pronunciation VARCHAR(100),
                definition TEXT,
                example_sentence TEXT,
                is_new BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_word (word)
            )
            """)

            # 4. Create day_words table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS day_words (
                id INT AUTO_INCREMENT PRIMARY KEY,
                day_id INT NOT NULL,
                word_id INT NOT NULL,
                word_order INT NOT NULL COMMENT '单词在当天列表中的顺序',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (day_id) REFERENCES days(id) ON DELETE CASCADE,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
                INDEX idx_day_word (day_id, word_order)
            )
            """)

            # 5. Create word_category table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS word_category (
                id INT AUTO_INCREMENT PRIMARY KEY,
                word_id INT NOT NULL,
                category_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
                UNIQUE KEY idx_word_category (word_id, category_id)
            )
            """)

            # 6. Create memory_progress table
            # Note: We reference the existing 'users' table which uses 'id' as PK
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                word_id INT NOT NULL,
                memory_strength FLOAT DEFAULT 0.0,
                review_count INT DEFAULT 0,
                last_reviewed TIMESTAMP NULL,
                next_review TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
                INDEX idx_user_word (user_id, word_id)
            )
            """)

            # --- Data Insertion ---
            
            # Check if data exists to avoid duplication
            cursor.execute("SELECT COUNT(*) as count FROM categories WHERE name='经济商业类词汇'")
            if cursor.fetchone()['count'] == 0:
                print("Inserting initial data...")
                
                # Insert Category
                cursor.execute("INSERT INTO categories (name, description) VALUES ('经济商业类词汇', '包含经济、商业、金融相关的基础词汇')")
                category_id = cursor.lastrowid

                # Insert Day 1
                cursor.execute("INSERT INTO days (week_number, day_number, title, description) VALUES (1, 1, 'Day 1', '第一周第一天，经济商业类词汇学习')")
                day_id = cursor.lastrowid

                # Insert Words
                words_data = [
                    ('economy', '/ˈkɒnəmi/', 'n. 节约；经济', True),
                    ('market', '/ˈmɑːkt/', 'v. 市场营销 n. 集市；市场；交易', True),
                    ('system', '/ˈsɪstəm/', 'n. (思想或理论)体系；系统；制度', True),
                    ('value', '/ˈvæljuː/', 'v. 重视，珍视；给……估价，给……定价 n. (商品)价值； (与价格相比的)值；是非标准，生活准则，价值观；值，数值', True),
                    ('rate', '/ret/', 'v. 评估，评价；划分等级 n. 速度，进度；比率；价格，费用；房产税', True),
                    ('estimate', '/ˈestɪmeɪt/', 'n. 估计，估价；评估 v. 估计，估价；评估', True),
                    ('assess', '/əˈses/', 'v. 评估，评定（性质、质量）；估算，估定（数量、价值）', True),
                    ('evaluate', '/iˈvæljueɪt/', 'v. 评估，评价', True),
                    ('weigh', '/weɪ/', 'v. 重量为……；称（重量）；权衡', True),
                    ('capital', '/ˈkæpt(ə)l/', 'n. 首都；资金；大写字母', True),
                    ('fund', '/fʌnd/', 'n. 资金；基金 v. 为……提供资金', True),
                    ('freeze', '/friːz/', 'v. 冻结；冷冻；停业；暂停 n. 冻结；冰冻（期）；霜冻', True),
                    ('invest', '/ɪnˈvest/', 'v. 投资；投入（精力）；授予，给予（权力等）', True),
                    ('risk', '/rɪsk/', 'n. 风险 n. 危险，风险；危险人物；借款人', True),
                    ('stake', '/steɪk/', 'n. 股本，股份；赌注；利害关系', True),
                    ('manipulate', '/məˈpɪleɪt/', 'v. 操作，处理；巧妙地控制；操纵', True),
                    ('stock', '/stɒk/', 'n. 资本，库存，现货；股票，公债', True),
                    ('share', '/ʃeər/', 'v. 分配，共用；分担 n. 一份，份额；股份', True),
                    ('bargain', '/ˈbæɡn/', 'v. 讨价还价，商讨条件 n. 减价品；便宜货；协议；交易', True),
                    ('dividend', '/ˈdɪvdənd/', 'n. 红利，股息；回报，效益；被除数', True),
                    ('currency', '/ˈkʌrənsi/', 'n. 流通，通货，货币', True),
                    ('monetary', '/ˈmɔːnətri/', 'adj. 货币的，金钱的；钱的；金融的；财政的', True),
                    ('budget', '/ˈbʌdʒɪt/', 'v. 谨慎花钱；把……编入预算 n. 预算；政府年度预算', True),
                    ('debt', '/det/', 'n. 债务', True),
                    ('credit', '/ˈkreɪdt/', 'v. 把……记入贷方；信任，相信；把……归于 n. 信用；学分；贷款', True),
                    ('loan', '/ləʊn/', 'n. 借出 n. 贷款；借款；借出', True),
                    ('mortgage', '/ˈmɔːɡreɪt/', 'n. 抵押，抵押品，抵押证明；抵押权，债权', True),
                    ('venture', '/ˈventʃə(r)/', 'v. 敢于去；小心地试，谨慎地做；冒着危险 n. 冒险，风险', True),
                    ('abundance', '/əˈbʌndəns/', 'n. 大量，丰富，富裕', True),
                    ('affluent', '/ˈæfluənt/', 'adj. 富裕的，富足的', True)
                ]

                for w in words_data:
                    # Insert word
                    cursor.execute("INSERT INTO words (word, pronunciation, definition, is_new) VALUES (%s, %s, %s, %s)", w)
                    word_id = cursor.lastrowid

                    # Link to Day 1
                    # We can use a counter or just append, but SQL example used ROW_NUMBER. 
                    # Here we just append. Order will be insertion order.
                    cursor.execute("INSERT INTO day_words (day_id, word_id, word_order) VALUES (%s, %s, %s)", (day_id, word_id, word_id)) # simple ordering

                    # Link to Category
                    cursor.execute("INSERT INTO word_category (word_id, category_id) VALUES (%s, %s)", (word_id, category_id))
            
            conn.commit()
            print("Database initialized successfully.")

    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()

if __name__ == "__main__":
    init_learning_db()
