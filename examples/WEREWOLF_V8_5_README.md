# 人狼ゲーム v8.5 - Hybrid Engine Edition

SSD Theory v8.0 の完全実装を使った人狼ゲームシミュレーション

## 特徴

### 🔄 **デュアルエンジン対応**
- **リファレンス実装** (`ssd_subjective_society`): 理論検証・詳細分析用
- **Nano実装** (`nano_core_engine`): プロダクション・高速実行用
- コマンドラインで簡単に切り替え可能

### 🧠 **v8理論の完全実装**
- **主観的観測**: 他者の内部状態（E, κ）は観測不可能
- **シグナル生成**: 観測可能な行動パターンから疑惑を推論
- **自己変化**: 疑惑・恐怖が心理状態（E, κ）に影響

### 🎮 **ゲームメカニクス**
- 役割: 村人、人狼、占い師
- フェーズ: 昼（議論・投票）、夜（襲撃・占い）
- 心理ダイナミクス:
  - **恐怖** (BASE層): 人狼の存在による圧力
  - **疑惑** (CORE層): 観測可能な行動から推論
  - **葛藤** (CORE/UPPER層): 疑惑 vs 信頼の内的闘争

## 使用方法

### 基本実行

```bash
# Nano実装で実行（デフォルト、高速）
python werewolf_game_v8_5.py

# リファレンス実装で実行（理論検証）
python werewolf_game_v8_5.py --engine reference

# 詳細ログ付き
python werewolf_game_v8_5.py --engine nano --verbose
```

### プレイヤー数・人狼数の調整

```bash
# 20人、人狼4人
python werewolf_game_v8_5.py --players 20 --werewolves 4

# 小規模ゲーム（7人、人狼2人）
python werewolf_game_v8_5.py --players 7 --werewolves 2 --verbose
```

### ベンチマーク比較

```bash
# リファレンス vs Nano の性能比較
python werewolf_game_v8_5.py --benchmark --players 20 --werewolves 4
```

## 実行例

### Nano実装（7人、詳細ログ）

```bash
$ python werewolf_game_v8_5.py --engine nano --players 7 --werewolves 2 --verbose

[Engine] Nano実装 (nano_core_engine)
  Player_0: werewolf
  Player_1: villager
  Player_2: villager
  Player_3: villager
  Player_4: werewolf
  Player_5: villager
  Player_6: seer

============================================================
  人狼ゲーム v8.5 開始
  プレイヤー: 7人
  人狼: 2人
============================================================

============================================================
  Day 1 - 議論フェーズ
============================================================

[観測可能な行動]

============================================================
  Day 1 - 投票フェーズ
============================================================
  Player_0 → Player_1 (疑惑: 0.00)
  Player_1 → Player_0 (疑惑: 0.00)
  ...

[処刑] Player_0 (役割: werewolf)

実行時間: 0.004秒
```

### ベンチマーク結果（20人）

```
[REFERENCE]
実行時間: 0.021秒
Day数: 8

[NANO]
実行時間: 0.013秒
Day数: 7

→ Nano実装が約1.6倍高速
```

## パフォーマンス比較

| プレイヤー数 | リファレンス実装 | Nano実装 | 速度比 |
|------------|----------------|---------|--------|
| 7人 | ~5ms | ~4ms | 1.25x |
| 20人 | ~21ms | ~13ms | **1.6x** |
| 100人（推定） | ~500ms | ~50ms | **10x** |

## オプション一覧

```
--engine {reference,nano}
    使用するエンジン
    reference: リファレンス実装（理論検証用）
    nano: Nano実装（高速実行用、デフォルト）

--players NUM
    プレイヤー数（デフォルト: 7）

--werewolves NUM
    人狼の数（デフォルト: 2）

--verbose
    詳細ログを表示
    - 各プレイヤーの観測可能な行動
    - 投票理由（疑惑レベル）
    - 占い結果

--benchmark
    両エンジンのベンチマーク比較を実行
```

## アーキテクチャ

### エンジンアダプターパターン

```python
AbstractEngineAdapter  # 共通インターフェース
    ↑
    ├─ ReferenceEngineAdapter  # ssd_subjective_society
    └─ NanoEngineAdapter       # nano_core_engine
```

### 心理状態の計算

1. **シグナル生成**: 内部状態（E, κ）→ 観測可能な行動
2. **疑惑計算**: 観測可能な行動 → 疑惑レベル
3. **圧力生成**: 疑惑・恐怖 → 心理的圧力
4. **状態更新**: 圧力 → E, κ の変化

### 投票ロジック

```python
def decide_vote(self, alive_players):
    # 全プレイヤーの疑惑を計算
    for candidate in candidates:
        suspicion = self.calculate_suspicion(candidate)
        # 観測可能な行動パターンから推論:
        # - 恐怖表情 → 人狼を知っている？
        # - 攻撃的行動 → 人狼の可能性
        # - 非協力的 → 疑わしい
        # - 規範違反 → 疑わしい
    
    # 最も疑わしいプレイヤーに投票
    return most_suspicious
```

## 理論的意義

### v8「主観的社会システム」の実証

✅ **主観的観測**: 他者の内部状態（E, κ）は直接観測不可能  
✅ **シグナル解釈**: 観測可能な行動から疑惑を主観的に推論  
✅ **自己変化**: 疑惑・恐怖が自己の心理状態を変化させる  
✅ **創発的ダイナミクス**: プログラムされた結果ではなく、主観的解釈の帰結

### リファレンス vs Nano の役割分担

| 実装 | 目的 | 用途 |
|------|------|------|
| **リファレンス** | 理論の完全性・抽象性 | 新機能の実験、理論検証、詳細分析 |
| **Nano** | パフォーマンス最適化 | プロダクション実行、大規模シミュレーション |

## 今後の拡張

- [ ] **記憶システム**: 過去の行動パターンを記憶し、疑惑を累積
- [ ] **会話生成**: LLMとの統合で自然言語での議論
- [ ] **役職追加**: 霊媒師、狩人、狂人など
- [ ] **グラフィカルUI**: 心理状態の可視化
- [ ] **マルチプレイヤー**: 人間プレイヤーとAIの混合

## ライセンス

SSD Theory v8.0 - Research Project

## 関連ファイル

- `ssd_core_engine.py`, `ssd_human_module.py`: リファレンス実装のコア
- `ssd_subjective_society.py`: Phase 8 主観的社会システム
- `nano_core_engine.py`: Nano実装（高速版）
- `demo_v8_final.py`: v8理論の完全デモ
