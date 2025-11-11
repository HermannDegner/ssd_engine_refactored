# SSD Engine Refactored

**Structural Subjectivity Dynamics (構造主観力学) 理論の実装**

## 📁 プロジェクト構造

```
ssd_engine_refactored/
├── 📂 core/                    - コアモジュール（安定版）
├── 📂 extensions/              - 拡張モジュール（実験的）
├── 📂 experimental/            - 実験的機能（検証段階）
├── 📂 examples/                - 実装例とデモ
├── 📂 docs/                    - 理論提案書
├── __init__.py
├── run_all_demos.py
└── README.md
```

## 🧠 SSD理論

**E/κダイナミクス**で人間の意思決定をモデル化:
- **E (未処理圧)**: 状況的・一時的な圧力
- **κ (慣性)**: 確立された価値・変化への抵抗
- **三層構造**: BASE（本能）/ CORE（自我）/ UPPER（戦略）

## 🚀 クイックスタート

```python
from ssd_engine_refactored.core import HumanAgent, HumanPressure

agent = HumanAgent()
pressure = HumanPressure()
pressure.base = 10.0
agent.step(pressure)
action = agent.get_action()
```

## 📚 ドキュメント

- **core/README.md** - コアモジュール詳細
- **extensions/README.md** - 拡張機能
- **experimental/README.md** - 実験的機能
- **examples/README.md** - 実装例集

## ⭐ 主要実装

### ゲームAI
**APEX SURVIVOR v3** - 純粋E/κ創発の完成版
- 本能的死の恐怖をκ初期値に反映
- 外部ロジックなしで安全行動が創発

詳細: `examples/apex_survivor_ssd_pure_v3.py`

### 社会分析 🆕
**社会現象の包括的分析** - 現実社会のダイナミクスをモデル化
- 意見分極化、リーダーシップの創発、規範形成
- 集団パニック、規範崩壊、カリスマ的リーダー
- SNS炎上、パワーハラスメント

**クイックスタート:**
```bash
python run_social_analysis.py
```

詳細: `examples/SOCIAL_ANALYSIS_README.md`

## 🎛️ SSD開発の実践的知見

### ⚠️ 重要：SSDの本質は「数値調整」
SSD理論は美しいが、実装は**泥臭いパラメータ調整作業**が全て。

#### ❌ 調整困難な設計パターン
```python
# 悪い例：パラメータが分散、内部値で調整
class Player:
    def __init__(self):
        self.agent.state.kappa[0] = 147.5  # 意味不明
        self.agent.state.kappa[1] = 8.2    # 影響度不明
```

#### ✅ 調整しやすい設計パターン  
```python
# 良い例：中央集約、直感的スケール
config = SSDConfig(
    survival_sensitivity=8.0,  # 0-10: 8=かなり敏感
    competition_drive=4.0,     # 0-10: 4=やや低い
    safety_weight=7.0          # 0-10: 7=安全重視
)
player = SSDPlayer(config)
```

### 🔧 必須機能
1. **パラメータ中央管理**: 全設定を1つのConfigクラスに
2. **0-10直感スケール**: エンジニアが理解できる範囲
3. **A/Bテスト機能**: 複数設定の同時比較
4. **自動最適化**: 目標メトリクス指定で自動調整
5. **設定保存/読込**: JSON形式でプリセット管理

参考実装: `examples/ssd_interactive_tuner.py`

### 📊 調整のベストプラクティス

#### 1. 段階的アプローチ
```python
# Step 1: 極端な設定で動作確認
cautious = SSDConfig(survival_sensitivity=9.0, safety_weight=9.0)
aggressive = SSDConfig(competition_drive=9.0, attack_weight=9.0)

# Step 2: A/Bテストで効果測定  
result = tester.compare([cautious, aggressive], test_situations)

# Step 3: 自動最適化で精密調整
optimal = tester.find_optimal(target_metrics={'choice_range': (2, 8)})
```

#### 2. 標準テストケース
```python
standard_situations = [
    {"name": "安全状況", "hp": 4, "rank": 2, "score_gap": 20},
    {"name": "危険状況", "hp": 1, "rank": 5, "score_gap": 100}, 
    {"name": "競争状況", "hp": 3, "rank": 2, "score_gap": 5}
]
```

#### 3. 期待される結果パターン
- **慎重型**: 選択2-4（常に安全寄り）
- **バランス型**: 選択3-7（状況に応じて変化）
- **攻撃型**: 選択5-9（常にリスク寄り）

### 💡 開発効率化のコツ
- **設定ファイル**: プリセットをJSONで管理
- **バッチテスト**: 複数設定を一括検証
- **可視化**: 結果をグラフ表示
- **回帰テスト**: 既知の動作パターンを自動検証

---

*SSDは理論的に美しいが、実装は数値調整が全て。調整しやすいコード構造が成功の鍵。*
