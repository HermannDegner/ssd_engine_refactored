# SSD Theory Examples - 実装例集

Structural Subjectivity Dynamics (SSD) 理論の実装例とデモプログラム

## 📁 フォルダ構成

```
examples/
├── 📄 apex_survivor_ssd_pure_v3.py    - APEX SURVIVOR完成版 ⭐
├── 📄 blackjack_ssd_pure.py           - Blackjack実装
├── 📄 roulette_ssd_pure.py            - Roulette実装
├── 📁 werewolf/                       - 人狼ゲーム各種実装
├── 📁 newtons_cradle/                 - ニュートンのゆりかご
├── 📁 demos/                          - 基本デモ集
└── 📁 archive/                        - 旧バージョン保管
```

## 🎮 ゲーム実装（ルートレベル）

### ⭐ **apex_survivor_ssd_pure_v3.py** (35.4KB)
**APEX SURVIVOR - 純粋E/κ創発の完成版**

「1位以外全員死亡」という極限状況で、外部ロジックなしに安全行動が創発する実装。

**主な特徴:**
- 本能的死の恐怖をκ初期値に反映（BASE κ=10-15）
- 外部制限なしでHP=1時に安全選択が創発
- 純粋なE/κダイナミクスの実証

**実行:**
```powershell
python apex_survivor_ssd_pure_v3.py
```

**理論的意義:**
v2からの根本的改善により、「死の恐怖は本能的（初期κ）、勝利欲求は後天的（低初期κ）」という設計原理を確立。

### **blackjack_ssd_pure.py** (27.6KB)
Blackjack（21）の実装

- ディーラー対プレイヤー
- Hit/Stand判断の創発
- 確率的思考の実装

### **roulette_ssd_pure.py** (29.4KB)
**Roulette - 確率パターン学習とκによる数字記憶**

偏りのあるルーレットで統計的パターンを学習する実装。

**主な特徴:**
- 数字の出現頻度をκで学習（`number_kappa[]`配列）
- 出た数字のκを強化、他を減衰させる相対学習
- 偏りなしモードでは「偏見育成場」として機能

**実行:**
```powershell
# 100%確実に7番が出る（極端なケース）
python roulette_ssd_pure.py --rounds 100 --bias-weight 9999

# 7番が10倍出やすい（現実的な偏り）
python roulette_ssd_pure.py --rounds 200 --bias-weight 10

# 通常モード（偏りなし）で偏見育成を観察
python roulette_ssd_pure.py --rounds 200 --biased-number 0 --bias-weight 1
```

**実験結果:**

| シナリオ | 7番出現率 | 7番κ値 | 結果 |
|---------|----------|--------|------|
| 100%固定（9999倍） | 100/100 (100%) | 10.50 | 全員が7番を学習、カジノ-364%ハウスエッジ |
| 10倍バイアス | 43/200 (21.5%) | 4.49 | 適度に学習、カジノ-51%ハウスエッジ |
| 通常（偏りなし） | - | 1.43(21番) | **偏見育成**: ランダムな偏りをパターンとして誤学習 |

**理論的意義:**
- κによる統計的学習の実証（出現頻度→慣性→選択確率）
- 人間の認知バイアス再現（パターン錯覚、確証バイアス）
- 探索と活用のバランス（赤黒も選びつつ、学習した数字も選ぶ）

## 📁 専門フォルダ

### 🐺 werewolf/
人狼ゲームの各種実装（5ファイル）

- **werewolf_ultimate_demo.py** - 究極デモ版（推奨）
- werewolf_extended_roles.py - 拡張役職版
- werewolf_narrator.py - ナレーター付き
- werewolf_visualizer.py - 可視化版
- visualize_werewolf_comparison.py - 比較分析

**詳細:** `werewolf/README.md`

### ⚙️ newtons_cradle/
ニュートンのゆりかご物理シミュレーション（3ファイル）

- **newtons_cradle_nano_animated.py** - 最新版（推奨）
- newtons_cradle_nano.py - 高精度版
- newtons_cradle_animated.py - 標準版

**詳細:** `newtons_cradle/README.md`

### 📚 demos/
基本デモプログラム集（7ファイル）

- demo_basic_engine.py - エンジン基礎
- demo_human_psychology.py - 人間心理モデル
- demo_pressure_system.py - 圧力システム
- demo_nonlinear_transfer.py - 非線形伝達
- demo_social_dynamics.py - 社会力学
- demo_subjective_social_pressure.py - 主観的社会圧
- demo_subjective_society.py - 主観的社会

**詳細:** `demos/README.md`

### 🗄️ archive/
旧バージョン保管（13ファイル）

開発過程で作成されたファイルを保管。

**詳細:** `archive/README.md`

## 🚀 クイックスタート

### 初めての方
```powershell
# 基本デモから開始
cd demos
python demo_basic_engine.py
```

### ゲームAIに興味がある方
```powershell
# APEX SURVIVOR（最も完成度が高い）
python apex_survivor_ssd_pure_v3.py
```

### 社会シミュレーションに興味がある方
```powershell
# 人狼ゲーム
cd werewolf
python werewolf_ultimate_demo.py
```

### 物理シミュレーションに興味がある方
```powershell
# Newton's Cradle
cd newtons_cradle
python newtons_cradle_nano_animated.py
```

## 🧠 SSD理論の基本概念

### 三層構造
- **BASE**: 本能的・生存的価値（死の恐怖、基本的欲求）
- **CORE**: 中核的・自我的価値（勝利欲求、自己実現）
- **UPPER**: 戦略的・理性的価値（状況分析、最適化）

### E/κダイナミクス
- **E（未処理圧）**: 状況から生じる一時的な圧力
- **κ（慣性）**: 確立された価値・変化への抵抗
- **β（減衰）**: 圧力の自然減衰係数

### 創発原理
**外部ロジックなし**で、E/κの内部力学から行動が創発する。

## 📖 推奨学習パス

1. **基礎理解** → `demos/demo_basic_engine.py`
2. **人間モデル** → `demos/demo_human_psychology.py`
3. **圧力システム** → `demos/demo_pressure_system.py`
4. **簡単なゲーム** → `blackjack_ssd_pure.py`
5. **複雑なゲーム** → `apex_survivor_ssd_pure_v3.py` ⭐
6. **社会システム** → `werewolf/werewolf_ultimate_demo.py`
7. **物理適用** → `newtons_cradle/newtons_cradle_nano_animated.py`

## 🎯 各実装の特徴比較

| 実装 | 複雑度 | 創発性 | 推奨用途 |
|------|--------|--------|----------|
| APEX SURVIVOR v3 | 高 | ⭐⭐⭐ | 理論実証 |
| Werewolf | 高 | ⭐⭐⭐ | 社会AI |
| Blackjack | 中 | ⭐⭐ | 基本ゲームAI |
| Roulette | 中 | ⭐⭐ | 確率的判断 |
| Newton's Cradle | 中 | ⭐⭐ | 物理応用 |
| Demos | 低 | ⭐ | 学習・理解 |

## 💡 開発のヒント

### 新しいゲーム実装を作る場合

1. **状況を意味圧に変換** - `_calculate_pressure()`
2. **κ初期値を設計** - 本能的 vs 後天的を区別
3. **外部ロジックを排除** - E/κから創発させる
4. **デバッグ出力を充実** - E/κ/action値を表示

### 重要な設計原則

**❌ 悪い例:**
```python
if self.hp == 1:
    choice = min(choice, 5)  # 外部制限
```

**✅ 良い例:**
```python
# HP=1時の圧力を意味圧に変換
pressure.base += 400  # 死の恐怖
# κ初期値: BASE=10-15（本能的恐怖）
# → E/κバランスから安全選択が創発
```

## 🎛️ パラメータ調整のベストプラクティス

### ⚠️ SSDの現実 - "結局は数値調整"

**SSD理論は美しいが、実装の成功は99%パラメータ調整にかかっている。**

理論的エレガンスと実装の現実のギャップを理解し、調整しやすい構造設計が重要。

### よくある失敗パターン

#### ❌ パラメータ分散問題
```python
# 悪い例：各クラスにパラメータが分散
class Player:
    def __init__(self):
        self.agent.state.kappa[0] = 147.5  # どこから来た数字？
        self.some_config.threshold = 23.7  # 他のクラスにも設定
        
def make_choice(self):
    magic_number = 800.0  # ハードコード！
    pressure.base += magic_number
```

**問題点:**
- パラメータの意味・影響度が不明
- 調整時に複数ファイルを修正が必要
- A/Bテストが困難
- 設定の保存・共有ができない

#### ❌ 内部値スケール問題
```python
# 悪い例：内部値で直接調整
kappa_base = 147.83429  # 意味不明な精密値
E_threshold = 0.000234  # 極小値
pressure_scale = 4847.2 # 謎の巨大数
```

**問題点:**
- 直感的でない（8.5と8.6の違いが分からない）
- 初心者に理解不可能
- 調整時の影響予測が困難

### ✅ 推奨パターン

#### 1. パラメータ中央集約管理
```python
@dataclass
class SSDConfig:
    # 直感的な0-10スケール
    survival_sensitivity: float = 5.0  # 生存への敏感さ
    competition_drive: float = 5.0     # 競争心の強さ
    strategic_thinking: float = 5.0    # 戦略思考レベル
    
    def to_internal(self) -> dict:
        # 内部パラメータに自動変換
        return {
            'kappa_base': self.scale(self.survival_sensitivity, 5, 50),
            'pressure_mult': self.scale(self.competition_drive, 100, 1000)
        }

# 使用時
config = SSDConfig(survival_sensitivity=8.0)  # 8/10 = かなり敏感
player = SSDPlayer(config)
```

#### 2. A/Bテスト対応
```python
# 複数設定の同時比較
configs = [
    SSDConfig(name="慎重型", survival_sensitivity=8.0, safety_weight=8.0),
    SSDConfig(name="攻撃型", competition_drive=8.0, attack_weight=8.0),
    SSDConfig(name="バランス", survival_sensitivity=5.0, competition_drive=5.0)
]

results = tester.compare_configs(configs, test_situations)
print(f"Best config: {results.best_config.name}")
```

#### 3. 期待される行動パターン
```python
expected_patterns = {
    "慎重型": {
        "安全状況": (2, 4),    # 選択2-4の範囲
        "危険状況": (1, 3),    # より慎重に
        "競争状況": (2, 5)     # 慎重だが参加
    },
    "攻撃型": {
        "安全状況": (5, 8),    # 選択5-8の範囲
        "危険状況": (3, 7),    # やや抑制
        "競争状況": (6, 9)     # 積極的
    }
}
```

### 🧪 パラメータ調整用ツール

#### インタラクティブ調整システム
```python
# ssd_interactive_tuner.py を使用
python ssd_interactive_tuner.py
```

**機能:**
- 0-10の直感的スケール
- リアルタイム結果表示
- A/Bテスト機能
- 自動最適化
- 設定保存/読込

#### パラメータ管理システム
```python
# ssd_parameter_tuning_system.py を使用
python ssd_parameter_tuning_system.py
```

**機能:**
- 中央集約型設定管理
- 内部値への自動変換
- プリセット管理
- バッチテスト実行

### 🎯 調整のコツ

#### Step 1: まず極端値で動作確認
```python
# 極端な設定で明確な違いを確認
cautious = SSDConfig(survival_sensitivity=9.0, competition_drive=1.0)
aggressive = SSDConfig(survival_sensitivity=1.0, competition_drive=9.0)
```

#### Step 2: 中間値で細かい調整
```python
# 動作が確認できたら中間値で調整
balanced = SSDConfig(survival_sensitivity=5.0, competition_drive=5.0)
```

#### Step 3: A/Bテストで最適化
```python
# 複数の候補から最適なものを選択
candidates = [config1, config2, config3]
best = optimizer.find_best(candidates, test_scenarios)
```

### ⚠️ よくあるトラブルと解決法

#### Q: 全員が同じ選択をしてしまう
**A:** κ値とE値のスケールが合っていない
```python
# 解決策：影響度を調整
safety_effect = -safety_drive * (self.safety_weight / 10) * 0.5  # 係数を調整
```

#### Q: 極端な選択（1or10）しか出ない
**A:** 創発関数の係数が大きすぎる
```python
# 解決策：係数を小さく
base_choice = 5.0
safety_pull = -survival * 0.3  # 0.3 → 0.1等に減少
```

#### Q: 個性の違いが出ない
**A:** パラメータ差が小さすぎる
```python
# 解決策：個性を極端に
cautious = SSDConfig(survival_sensitivity=9.0)  # 5.0 → 9.0
aggressive = SSDConfig(competition_drive=9.0)   # 5.0 → 9.0
```

### 📋 新実装時のチェックリスト

#### 必須機能
- [ ] 中央集約型パラメータ管理
- [ ] 0-10の直感的スケール
- [ ] A/Bテスト機能
- [ ] 設定保存/読込（JSON）
- [ ] 期待パターンとの照合

#### 推奨機能
- [ ] 自動最適化機能
- [ ] リアルタイム可視化
- [ ] 回帰テスト
- [ ] プリセット管理
- [ ] バッチ実行機能

#### 避けるべきパターン
- [ ] ハードコードされたマジックナンバー
- [ ] パラメータの分散配置
- [ ] 内部値での直接調整
- [ ] A/Bテストができない構造
- [ ] 設定共有ができない実装

**結論: SSDは理論は美しいが、実装は数値調整が全て。調整しやすいインフラ設計が成功の鍵。**

## 🌡️ 熱力学的SSDシステム

### 概要
心理状態を「体温」として表現し、熱ノイズによる決断の揺らぎを実現。

### 実装例: `apex_survivor_thermal_v1.py`
```bash
python examples/apex_survivor_thermal_v1.py
```

### 熱力学的効果

#### 1. **心理状態 → 体温変化**
```python
# ストレスと意味圧強度から体温計算
pressure_factor = pressure_intensity / 500.0  # 0-2倍
stress_factor = stress_level * 4.0            # 最大+4度
target_temp = base_temp + pressure_factor + stress_factor
```

#### 2. **体温による行動変化**
- **低体温（35-37°C）**: 冷静、計算的判断
- **微熱（37-39°C）**: やや積極的だが安定
- **発熱（39-42°C）**: 衝動的、極端な選択

#### 3. **熱ノイズによる揺らぎ**
```python
# 体温に比例した決断の揺らぎ
thermal_noise = np.random.normal(0, temperature * 0.1)
choice += thermal_noise
```

### 観察された行動パターン

| 性格 | 平常時 | 微熱時 | 発熱時 |
|------|--------|--------|--------|
| 慎重派 | 選択1-3 | 選択2-4 | 選択1-3（極度慎重） |
| 攻撃派 | 選択5-7 | 選択6-8 | 選択7-10（衝動的） |
| バランス | 選択3-6 | 選択4-7 | 選択6-8（激しい） |

### 熱力学的解釈
- **体温 = 心理的興奮度**（死の恐怖、勝利欲求、競争圧）
- **熱ノイズ = 感情の揺らぎ**（直感的判断、衝動）
- **温度上昇 = ストレス反応**（危機感、競争激化）
- **温度低下 = 冷静化**（理性的判断、計算思考）

### 設計のポイント

#### ✅ 良い熱設計
```python
class ThermalHumanAgent(HumanAgent):
    def __init__(self):
        self.base_temperature = 37.0  # 個体差考慮
        self.current_temperature = self.base_temperature
        
    def update_temperature(self, pressure, stress):
        # 生理学的範囲内での変動（35-42°C）
        target = self.base_temperature + pressure_factor + stress_factor
        self.current_temperature = np.clip(target, 35.0, 42.0)
```

#### ❌ 避けるべきパターン
```python
# 悪い例：非現実的な温度
temperature = 100.0  # 人間は死ぬ
temperature = -10.0  # 物理的に不可能

# 悪い例：体温と行動の関連性なし
choice = random.randint(1, 10)  # 体温無視
```

### 応用可能性
- **ゲームAI**: プレッシャーによる判断力変化
- **社会シミュレーション**: 集団ヒステリア、パニック現象
- **教育システム**: 学習ストレスとパフォーマンス
- **意思決定支援**: 感情状態を考慮した推奨システム

**効果**: より生物学的で自然な行動変化、人間らしい決断の揺らぎを実現。**

## 📚 関連ドキュメント

- `archive/README.md` - 設計変更の履歴
- `werewolf/README.md` - 人狼ゲーム詳細
- `newtons_cradle/README.md` - 物理シミュレーション詳細
- `demos/README.md` - デモプログラム学習ガイド

## 🔬 研究用途

これらの実装は以下の研究に使用できます:

- ゲームAIの創発的行動生成
- 社会シミュレーションの主観的モデリング
- 物理システムのSSD的記述
- 意思決定の多層的モデル化

---

**Note:** すべての実装は純粋なE/κ創発原理に基づいています。外部ロジックによる行動制御は避け、内部力学から行動が自然に生まれる設計を目指しています。
