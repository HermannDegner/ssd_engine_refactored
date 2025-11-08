# SSD Theory - Extensions

拡張モジュール - 社会システムと高度な機能

## 📦 モジュール一覧

### 社会的相互作用

#### **ssd_social_dynamics.py** (14.6KB)
社会的力学の基礎

**主要クラス:**
- `SocialAgent` - 社会的エージェント
- `SocialNetwork` - エージェント間ネットワーク

**機能:**
- マルチエージェントシステム
- エージェント間相互作用
- 集団行動の創発
- 社会的影響の伝播

#### **ssd_subjective_social_pressure.py** (14.0KB)
主観的社会圧モデル

**主要クラス:**
- `SubjectiveSocialPressure` - 主観的社会圧力

**機能:**
- 個人視点の社会認識
- 他者からの圧力の主観的評価
- 社会的文脈の影響
- 立場による圧力の非対称性

#### **ssd_subjective_society.py** (18.7KB)
主観的社会システム

**主要クラス:**
- `SubjectiveSociety` - 主観的社会全体

**機能:**
- 社会全体の主観的構築
- 複数視点の統合
- 集合的主観の創発
- 社会的均衡の形成

### 高度な機能

#### **ssd_dynamic_interpretation.py** (19.3KB)
動的解釈システム（V9提案）

**主要クラス:**
- `DynamicInterpreter` - 動的解釈器

**機能:**
- 状況の動的解釈
- 文脈依存的意味付け
- 解釈の学習と更新
- メタ認知的処理

**理論的背景:**
`../docs/V9_DYNAMIC_INTERPRETATION_PROPOSAL.md` 参照

#### **ssd_memory_structure.py** (19.9KB)
記憶構造システム（V10提案）- **メタ整合慣性システムの実装**

**主要クラス:**
- `StructuredMemoryStore` - 構造化記憶ストア（メタκシステムの中核）
- `MemoryCluster` - 記憶クラスタ（メタ整合慣性 κ^(meta) の実体）
- `Concept` - 抽出された概念（抽象化言語）

**機能:**
- 類似記憶の自動クラスタリング（二次学習）
- プロトタイプ（典型例）の形成（メタκ）
- 概念の自動抽出と命名（抽象化言語）
- 概念ベースの高速推論（圧縮による効率化）
- 説明可能性の向上（パターンの言語化）

**理論的背景:**
- **SSD理論:** メタ整合慣性システム（Meta-Alignment Inertia System）
  - 個別の記憶（κᵢ）を上位パターン（κ^(meta)）へ圧縮
  - 二次学習: dκ^(meta)/dt = η_m f({κᵢ}, p, E)
  - 人間知性の本質: 物語的パターン化の実装
  
- **心理学的基盤:**
  - Roschのプロトタイプ理論
  - ポランニーの暗黙知（tacit → explicit knowledge）
  - ピアジェの図式（schema）形成

- **ドキュメント:**
  - `../docs/V10_MEMORY_STRUCTURE_PROPOSAL.md`
  - 元理論: [人間モジュール　メタ整合慣性システム(抽象化).md](https://github.com/HermannDegner/Structural-Subjectivity-Dynamics/blob/main/Human_Module/人間モジュール　メタ整合慣性システム(抽象化).md)

## 🌐 社会システムの実装

### 基本的な使用

```python
from ssd_engine_refactored.extensions import SocialAgent, SocialNetwork

# エージェント作成
agents = [SocialAgent(f"Agent_{i}") for i in range(5)]

# ネットワーク構築
network = SocialNetwork(agents)
network.add_connection(agents[0], agents[1], strength=0.8)

# 相互作用シミュレーション
for step in range(100):
    network.update()
```

### 人狼ゲームへの適用

```python
from ssd_engine_refactored.extensions import SubjectiveSocialPressure

# 各プレイヤーの主観的社会認識
def calculate_suspicion_pressure(player, others):
    pressure = SubjectiveSocialPressure()
    
    for other in others:
        # 他者からの疑いを主観的に評価
        suspicion = player.perceive_suspicion(other)
        pressure.add_pressure(other, suspicion)
    
    return pressure
```

## 🧠 理論的拡張

### 主観性の実装

**個人の主観:**
- 同じ状況でも人により異なる解釈
- 立場・役割による認識の違い
- 過去の経験による影響

**集合的主観:**
- 複数の主観が相互作用
- 社会的均衡の創発
- 共有認識の形成

### 動的解釈（V9）

従来の固定的意味圧ではなく、**状況を動的に解釈**：

```python
# 固定的（従来）
if hp == 1:
    pressure.base = 400  # 常に400

# 動的（V9）
interpreter = DynamicInterpreter()
pressure = interpreter.interpret_situation({
    'hp': 1,
    'rank': 5,
    'rounds_left': 10
})  # 文脈全体から圧力を動的に生成
```

### 記憶構造（V10）

E/κに加えて**記憶**を導入：

```python
memory = MemoryStructure()

# 経験を記憶
memory.store(experience, importance=0.8)

# 想起が現在の圧力に影響
recalled = memory.recall(current_situation)
pressure += recalled.to_pressure()
```

## 🔗 依存関係

```
core/ (基本モジュール)
    ↓
extensions/
    ├── ssd_social_dynamics.py (マルチエージェント)
    ├── ssd_subjective_social_pressure.py (主観的圧力)
    ├── ssd_subjective_society.py (社会システム)
    ├── ssd_dynamic_interpretation.py (V9: 動的解釈)
    └── ssd_memory_structure.py (V10: 記憶)
```

## 🎯 使用例

### 人狼ゲーム
`../examples/werewolf/` で実装例を参照

### 社会シミュレーション
`../examples/demos/demo_subjective_society.py` で基本デモを参照

## 📚 研究提案

### V9: 動的解釈提案
**目的:** 固定的意味圧から動的解釈へ

**詳細:** `../docs/V9_DYNAMIC_INTERPRETATION_PROPOSAL.md`

**状態:** 実装済み、検証中

### V10: 記憶構造提案
**目的:** E/κに記憶システムを統合

**詳細:** `../docs/V10_MEMORY_STRUCTURE_PROPOSAL.md`

**状態:** 実装済み、検証中

## ⚠️ 注意事項

これらは**実験的拡張**です：

- コアモジュールより不安定
- API変更の可能性あり
- 十分な検証が必要

本番使用前に `core/` モジュールでの実装を推奨。

---

*Note: 社会システムと高度な機能の実験的実装*
