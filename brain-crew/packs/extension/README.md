# Extension Pack（扩展包）

Extension Pack 用于存放：

1. **调用频率低、但仍有特定价值的专家**
2. **新加入但尚未经过充分实测的专家**
3. **因数量膨胀需要从 core/brand/tech/enterprise/meta 中迁出的专家**

## 当前状态

当前 Brain Crew v1.0.0 的 30 位专家全部保留在原 5 个 pack 中。

基于 `docs/overlap-matrix.md` 的计算结果：
- 同 pack 内专家的最高重叠度为 0.28（段永平 vs 巴菲特 / 王阳明）
- 没有 ≥0.50 的高重叠配对
- 因此**本轮不做迁移**

## 未来迁移标准

当满足以下任一条件时，可考虑将专家移入 extension pack：

- 连续两个版本 Darwin 评分低于 85
- 与 pack 内其他专家标签重叠度 ≥0.50
- 在真实使用场景中 30 天内零调用
- 新增专家导致单 pack 人数超过建议上限（core ≤8, brand ≤8, tech ≤6, enterprise ≤12, meta ≤5）

## 迁移流程

1. 在 `expert-registry.json` 中修改该专家的 `pack` 字段为 `extension`
2. 移动目录 `packs/<原pack>/<expert-dir>/` 到 `packs/extension/<expert-dir>/`
3. 更新 frontmatter 中的 `pack` 字段
4. 重跑 `check-registry.sh`、`test-engine-integration.py`、`darwin-quick-score.py all`
