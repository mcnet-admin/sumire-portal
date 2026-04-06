name: 15:31 Daily Reservation Cleanup
on:
  schedule:
    - cron: '31 6 * * *'  # UTC 6:31 = 日本時間 15:31

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Generate Clean Report
        id: generate_report
        run: |
          REPORT=$(node scripts/daily_report.js)
          # 出力結果を環境変数に保存
          echo "REPORT_HTML<<EOF" >> $GITHUB_ENV
          echo "$REPORT" >> $GITHUB_ENV
          echo "EOF" >> $GITHUB_ENV

      - name: Send Email via SendGrid
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.sendgrid.net
          server_port: 465
          username: apikey
          password: ${{ secrets.SENDGRID_API_KEY }}
          subject: 【自動送信】明日（${{ env.targetStr }}）の確定予約リスト
          to: staff@mclean.ed.jp  # 園の共用アドレス
          from: system@mclean.ed.jp
          html_body: ${{ env.REPORT_HTML }}
