# SSD Engine - Structural Subjectivity Dynamics

**構造主観力学エンジン: 物理・社会・ゲームAIを統一する理論実装**

[![Theory](https://img.shields.io/badge/Theory-SSD-blue)](docs/)
[![Status](https://img.shields.io/badge/Status-Production-green)]()
[![Python](https://img.shields.io/badge/Python-3.11+-blue)]()

---

## 🌟 驚異の汎用性

**同一の理論的コア（E/κダイナミクス）で以下の全てを実現:**

| 領域 | 実装例 | 実証内容 |
|------|--------|----------|
| 🔬 **物理シミュレーション** | ニュートンの揺りかご | 運動量保存則の創発 |
| 🏛️ **社会ダイナミクス** | フランス革命、恐怖伝染 | 革命、規範形成、集団心理 |
| 🎮 **ゲームAI** | ブラックジャック、人狼 | 戦略学習、心理戦、協調と裏切り |

**実証デモ:** `python examples/ultimate_ssd_showcase.py`

---

## 💡 SSD理論の核心

### E/κダイナミクス

```
E（未処理圧力）: 外部圧力の蓄積量
κ（整合慣性）: 過去の経験から形成された行動傾向
跳躍（Leap）: E が閾値を超えた時の状態遷移
```

**物理的解釈:**
- E: 位置/運動エネルギー
- κ: 運動慣性
- 跳躍: 衝突による運動量移転

**社会的解釈:**
- E: 不満/恐怖/イデオロギーの蓄積
- κ: 社会規範、階級意識
- 跳躍: 革命、パニック、規範転換

**ゲーム的解釈:**
- E: リスク、ストレス、疑念
- κ: 学習した戦略、行動パターン
- 跳躍: 戦略変更、裏切り

---

## 🚀 クイックスタート

### インストール

```bash
git clone https://github.com/HermannDegner/ssd_engine_refactored.git
cd ssd_engine_refactored
```

### 基本的な使用

```python
from core.ssd_human_module import HumanAgent, HumanPressure

# エージェント作成
agent = HumanAgent(agent_id="Player1")

# 圧力を与える
pressure = HumanPressure()
pressure.base = 50.0    # 本能的圧力（恐怖、欲求）
pressure.core = 30.0    # 規範的圧力（義務、責任）
pressure.upper = 10.0   # 理念的圧力（信念、理想）

# 状態更新
agent.step(pressure=pressure, dt=0.1)

# 状態確認
print(f"E状態: {agent.state.E}")
print(f"κ状態: {agent.state.kappa}")
print(f"支配層: {agent.dominant_layer()}")
```

---

## 📚 実装例集

### 🎮 ゲームAI

#### **Apex Survivor** - バトルロイヤルAI
純粋なE/κダイナミクスから生存戦略が創発

```bash
python examples/apex_survivor_ssd_pure_v3.py
```

**特徴:**
- 外部ロジックなし、純粋な内部力学
- 本能的な死の恐怖 → 安全行動の創発
- κ構造の個人差 → 多様なプレイスタイル

#### **ブラックジャック** - リスク評価AI
手札の状態からリスクを本能的に評価

```bash
python examples/blackjack_ssd_pure.py
```

**特徴:**
- リスク → BASE層のE蓄積
- 学習した戦略 → CORE層のκ
- 経験による戦略最適化

#### **人狼ゲーム** - 心理戦AI
嘘の罪悪感、疑念の検出

```bash
python examples/werewolf/werewolf_ultimate_demo.py
```

**特徴:**
- 占い結果 → 概念記憶の形成
- 罪悪感 → CORE層のE蓄積
- 疑念 → BASE層の本能的警戒

### 🏛️ 社会シミュレーション

#### **フランス革命**
階級闘争と体制転換のダイナミクス

```bash
python examples/french_revolution_simulator.py
```

**実証内容:**
- 不満の蓄積 → 革命の跳躍
- 階級間の競争的カップリング
- テロルの時代の再現

#### **社会現象分析**
現代社会の包括的モデル化

```bash
python run_social_analysis.py
```

**分析内容:**
- 意見分極化、リーダーシップの創発
- 集団パニック、規範崩壊
- SNS炎上、パワーハラスメント

### 🔬 物理シミュレーション

#### **ニュートンの揺りかご**
運動量保存則の創発的再現

```bash
python examples/newtons_cradle/newtons_cradle_animated.py
```

**特徴:**
- 位置エネルギー → E
- 運動慣性 → κ
- 衝突 → 層間エネルギー転送

---

## 🏗️ プロジェクト構造

```
ssd_engine_refactored/
├── 📂 core/                          # コアエンジン（安定版）
│   ├── ssd_core_engine.py           # E/κダイナミクスの基本実装
│   ├── ssd_human_module.py          # 四層人間心理モデル
│   ├── ssd_pressure_system.py       # 多次元意味圧システム
│   └── ssd_nonlinear_transfer.py    # 非線形層間転送
│
├── 📂 extensions/                    # 拡張機能
│   ├── ssd_social_dynamics.py       # 社会的カップリング
│   ├── ssd_memory_structure.py      # 構造化記憶システム
│   ├── ssd_subjective_society.py    # 主観的社会モデル
│   └── ssd_dynamic_interpretation.py # 動的解釈システム
│
├── 📂 examples/                      # 実装例
│   ├── apex_survivor_ssd_pure_v3.py # バトルロイヤルAI
│   ├── blackjack_ssd_pure.py        # ブラックジャックAI
│   ├── roulette_ssd_pure.py         # ルーレットAI
│   ├── french_revolution_simulator.py # 革命シミュレーター
│   ├── ultimate_ssd_showcase.py     # 🌟 究極のショーケース
│   ├── werewolf/                    # 人狼ゲームAI
│   ├── newtons_cradle/              # 物理シミュレーション
│   └── demos/                       # 理論デモ集
│
├── 📂 experimental/                  # 実験的機能
└── 📂 docs/                          # 理論文書
```

---

## 🎯 理論的背景

### 四層構造の心理モデル

```
PHYSICAL層 (R=1000) - 身体的状態
    ↕
BASE層 (R=100)      - 本能（恐怖、欲求、快楽）
    ↕
CORE層 (R=10)       - 自我（規範、義務、責任）
    ↕
UPPER層 (R=1)       - 理性（理念、戦略、信念）
```

**R値**: 抵抗値（大きいほど安定、小さいほど不安定）

### 社会的カップリング

```python
# エネルギー伝播
ΔE_i = Σ ζ_ij * (E_j - E_i)

# κ伝播（規範の学習）
Δκ_i = Σ ξ_ij * (κ_j - κ_i)

# 競争による増幅
if relationship < 0:
    ΔE_i *= (1 + ω * |relationship|)
```

**パラメータ:**
- ζ (zeta): エネルギー伝播係数
- ξ (xi): κ伝播係数
- ω (omega): 競争増幅係数

---

## 📖 詳細ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| [core/README.md](core/README.md) | コアモジュール詳細 |
| [extensions/README.md](extensions/README.md) | 拡張機能の説明 |
| [examples/README.md](examples/README.md) | 実装例の一覧 |
| [docs/](docs/) | 理論提案書 |

---

## 🔬 実証結果

### 物理シミュレーション
✅ **ニュートンの揺りかご**: 運動量保存則が自然に創発
- 左端の球を持ち上げる → 右端の球が跳ね上がる
- E/κダイナミクスによる運動量移転の再現

### 社会ダイナミクス
✅ **フランス革命**: 歴史的経過の再現
- 平民の不満蓄積 → 革命の跳躍
- テロルの時代 → 恐怖伝染の創発
- 階級間の競争的カップリング

✅ **恐怖伝染**: 協力関係を通じた感情伝播
- 1人の恐怖 → 5人全員に伝播（3ステップで完了）
- 社会的カップリング係数 ζ = 0.3

### ゲームAI
✅ **Apex Survivor**: 純粋創発による生存戦略
- 外部ロジックなし
- 生存率 84% (21/25 生存)
- 個人差のあるκ構造 → 多様な戦略

✅ **ブラックジャック**: 学習による戦略最適化
- 初期: κ_CORE = 1.00 (無学習)
- 学習後: κ_CORE = 1.13 (慎重戦略の定着)

---

## 🌟 究極のショーケース

**物理、社会、ゲームAI - 全て同じエンジンで動く実証デモ**

```bash
python examples/ultimate_ssd_showcase.py
```

このデモは、同一のE/κダイナミクスで以下を統一的に記述できることを実証します:

1. **物理現象**: ニュートンの揺りかご（運動量保存）
2. **社会現象**: 革命、恐怖伝染、規範形成
3. **ゲームAI**: 戦略学習、心理戦、協調と裏切り

**誰が信じるだろうか？** → このデモを実行した人なら信じます。

---

## 🛠️ 開発・貢献

### 環境要件

- Python 3.11+
- NumPy
- Matplotlib (可視化用)
- Numba (高速化用、オプション)

### テスト実行

全てのデモを一括実行:
```bash
python run_all_demos.py
```

社会分析デモのみ:
```bash
python run_social_analysis.py
```

---

## 📜 ライセンス

このプロジェクトは研究目的で公開されています。

---

## 📬 コンタクト

**作成者**: Hermann Degner  
**リポジトリ**: [ssd_engine_refactored](https://github.com/HermannDegner/ssd_engine_refactored)

---

## 🎓 引用

このエンジンを研究に使用する場合は、以下を引用してください:

```
SSD Engine - Structural Subjectivity Dynamics
A unified framework for physics, social dynamics, and game AI
https://github.com/HermannDegner/ssd_engine_refactored
```

---

**🌟 これがSSD（構造主観力学）の力です。**

*一つの理論で、物理・社会・心理を統一的に記述する*
