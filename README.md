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

---

*Note: 外部ロジックなしに、純粋な内部力学から行動を創発させる理論実装*
