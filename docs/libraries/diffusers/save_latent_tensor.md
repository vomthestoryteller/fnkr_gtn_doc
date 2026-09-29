# Save Latent Tensor

**`LatentArtifact`를 PyTorch `.pt` 파일로 디스크에 저장합니다. 디버깅이나 오프라인 테스트 픽스처(fixture) 구축에 유용합니다.**

카테고리: `ModularDiffusion/IO`

## 어떤 노드인가요?

- 디코딩된 이미지가 아니라 순수 잠재(latent) 텐서를 저장합니다. 워크플로우로 다시 불러오려면 `torch.load(...)`로 `.pt`를 로드하고 `LatentArtifact`로 래핑하거나 커스텀 코드에서 직접 사용하세요.
- 출력 포트(`saved_path`)는 확인된 절대 경로이므로 로깅 또는 메타데이터 노드에 연결할 수 있습니다.

## 일반적인 워크플로우 위치

```text
Generate Media Latents → [Save Latent Tensor]
                       └→ Decode Media Latent → Save Image
```

## 노드 미리보기

<!-- TODO: docs/assets/nodes/save-latent-tensor.png 스크린샷 추가 예정 -->

### 입력 (Inputs)

| 이름 | 유형 | 필수 여부 | 설명 |
| --- | --- | --- | --- |
| `latent_tensor` | `LatentArtifact` | 예 | 저장할 잠재 텐서입니다. |

### 출력 (Outputs)

| 이름 | 유형 | 설명 |
| --- | --- | --- |
| `saved_path` | str | 텐서가 기록된 절대 경로입니다. |

### 파라미터 (Parameters)

| 이름 | 유형 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `file_path` | str | `debug/latent.pt` | 출력 경로입니다. 상대 경로는 워크스페이스 디렉토리를 기준으로 확인되며 상위 폴더는 자동으로 생성됩니다. |

## 팁 및 주의사항

- **텐서는 저장 전에 분리(detach)되어 CPU로 이동됩니다** — 모든 디바이스에서 안전하게 다시 로드할 수 있습니다.
- 순수 텐서 외에는 **메타데이터가 저장되지 않습니다.** 잠재 텐서 언패킹에 사용되는 `source_shape`를 다시 불러와야 하는 경우 별도로 기록하세요.
- **`.pt` 파일은 용량이 큽니다.** 1024×1024 SDXL 잠재 텐서는 약 4MB이며, LTX 비디오 잠재 텐서는 수백 MB에 달할 수 있습니다.

## 관련 항목

- [Generate Media Latents](generate_media_latents.md) — 일반적인 업스트림 노드.\n
