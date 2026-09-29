# Decode Media Latent

**잠재 텐서에 대해 파이프라인의 VAE 디코더를 실행하여 이미지 또는 비디오를 생성합니다 — 일반적으로 워크플로우의 마지막 노드입니다.**

카테고리: `ModularDiffusion/Encode\Decode`

## 어떤 노드인가요?

- 출력이 **동적**입니다: 이미지 파이프라인의 경우 `output_image`, 비디오 파이프라인(LTX, LTX2, WAN)의 경우 `output_video` (+ `fps`)로 전환됩니다. `pipeline`을 연결하면 자동으로 바뀝니다.
- 거의 항상 워크플로우의 마지막 노드로 사용됩니다. 다운스트림의 Save Image / Save Video 노드에 연결하세요.

## 일반적인 워크플로우 위치

```text
Generate Media Latents → [Decode Media Latent] → Save Image / Save Video
```

## 노드 미리보기

<img src="../assets/nodes/decode-media-latent.png" alt="Decode Media Latent" width="480">

### 입력 (Inputs)

| 이름 | 유형 | 필수 여부 | 설명 |
| --- | --- | --- | --- |
| `pipeline` | `Pipeline Config` | 예 | 잠재 텐서를 생성한 파이프라인과 일치해야 합니다. |
| `latent_tensor` | `LatentArtifact` | 예 | 디코딩할 잠재 텐서입니다. |

### 출력 (Outputs)

| 이름 | 유형 | 설명 |
| --- | --- | --- |
| `output_image` | `ImageArtifact` | 이미지 파이프라인용 출력입니다. |
| `output_video` | `VideoUrlArtifact` | 비디오 파이프라인용 출력입니다. |

### 파라미터 (Parameters)

| 이름 | 유형 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `fps` | int (1–120) | `25` | 출력 프레임 레이트. **비디오 파이프라인에서만 표시됩니다.** |

## 팁 및 주의사항

- **잠재 텐서를 생성한 동일한 파이프라인을 사용하세요.** 각 파이프라인에는 학습된 고유 VAE가 포함되어 있으므로 일치하지 않는 VAE로 디코딩하면 결과물이 깨집니다.
- **큰 잠재 텐서는 디코딩 시 더 많은 VRAM을 필요로 합니다.** 고해상도 또는 다중 프레임 잠재 텐서는 디코딩 중 더 많은 메모리가 필요합니다. 배치 단위로 디코딩하여 최대 VRAM 사용량을 낮추려면 Pipeline Builder에서 `vae_slicing`을 활성화하세요.

## 관련 항목

- [Encode Media Latent](encode_media_latent.md) — 역연산 노드.
- [Generate Media Latents](generate_media_latents.md) — 일반적인 업스트림 노드.

