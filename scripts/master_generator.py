import pandas as pd
import json
import os

def generate_master_files():
    # 設定: ファイルパス
    input_file = 'data/finalDB.xlsx'
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 1. クラスコード読み込み (シート名: クラスコード)
        # 1列目: コード(HY1等), 2列目: 和名(ひよこ1組等) を想定
        df_codes = pd.read_excel(input_file, sheet_name='クラスコード')
        cols = df_codes.columns
        code_map = dict(zip(df_codes[cols[0]].astype(str), df_codes[cols[1]]))

        # 2. 園児名簿読み込み (シート名: 園児名簿)
        df_students = pd.read_excel(input_file, sheet_name='園児名簿')
        student_master = {}
        
        for _, row in df_students.iterrows():
            # クラス名の変換
            raw_cls = str(row['class'])  # Excelの 'class' 列
            kanji_cls = code_map.get(raw_cls, "")
            
            if kanji_cls:
                display_cls = f"{kanji_cls} ({raw_cls})"
            else:
                display_cls = raw_cls
            
            # メールアドレスの取得とクリーニング (NaN対策)
            # email_01, email_02 列から取得。空なら空文字にする。
            e01 = str(row.get('email_01', "")).strip()
            e02 = str(row.get('email_02', "")).strip()
            
            # Pandas特有の "nan" 文字列を空文字に変換
            e01 = "" if e01.lower() == "nan" else e01
            e02 = "" if e02.lower() == "nan" else e02
            
            if display_cls not in student_master:
                student_master[display_cls] = []
            
            # JSON構造に格納
            student_master[display_cls].append({
                'id': str(row['student_id']), 
                'name': str(row['name']), 
                'parent_email01': e01,
                'parent_email02': e02
            })
        
        # students.json として保存
        with open(f'{output_dir}/students.json', 'w', encoding='utf-8') as f:
            json.dump(student_master, f, ensure_ascii=False, indent=2)

        # 3. 休日・休暇期間の展開 (シート名: 休日一覧)
        # ヘッダーが2行目(index 1)にある想定
        df_h = pd.read_excel(input_file, sheet_name='休日一覧', header=1)
        all_holidays = set()
        
        # 「日付」列（単発の休み）
        if '日付' in df_h.columns:
            all_holidays.update(df_h['日付'].dropna().dt.strftime('%Y-%m-%d').tolist())
            
        # 「開始日」「終了日」列（長期休暇など）
        if '開始日' in df_h.columns and '終了日' in df_h.columns:
            for _, row in df_h[['開始日', '終了日']].dropna().iterrows():
                r = pd.date_range(start=row['開始日'], end=row['終了日'])
                all_holidays.update(r.strftime('%Y-%m-%d').tolist())

        # holidays.json として保存
        with open(f'{output_dir}/holidays.json', 'w', encoding='utf-8') as f:
            json.dump(sorted(list(all_holidays)), f, ensure_ascii=False, indent=2)
        
        print("✅ 処理成功: output/ フォルダに students.json と holidays.json を作成しました")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    generate_master_files()