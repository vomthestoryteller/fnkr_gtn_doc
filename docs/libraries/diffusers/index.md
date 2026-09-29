# Diffusers 라이브러리 (Diffusers Library)

모듈형 🧨 [Diffusers](https://huggingface.co/docs/diffusers/index) 파이프라인으로 유연한 미디어 생성 워크플로우를 구축하세요.

Diffusers 라이브러리는 디퓨전(diffusion) 실행 과정을 더욱 정밀하게 제어하고자 하는 제작자를 위해 설계되었습니다. 고정된 일체형 "이미지 생성" 단계를 실행하는 대신, 디퓨전 프로세스를 개별적으로 연결 가능한 단계로 분할하여 파이프라인의 각 부분을 검사, 재사용 및 맞춤 설정할 수 있습니다.

!!! warning "실험적 기능 — 활발히 개발 중"

    API, 노드 인터페이스, 워크플로우 템플릿 및 라이브러리 구조는 예고 없이 언제든지 변경될 수 있으며 마이그레이션을 지원하지 않을 수 있습니다. 안정성이 필요한 경우 특정 커밋에 고정(pin)하고, 업데이트 시 호환성이 깨질 수 있음을 감안하세요.

- **리포지토리**: [griptape-ai/griptape-nodes-library-diffusers](https://github.com/griptape-ai/griptape-nodes-library-diffusers)
- **요구 사항**: GPU 지원 환경 (**CUDA** 또는 **MPS**)
- **노드 카테고리**: 노드 선택기(node picker) 내 `ModularDiffusion/…`

## 설치 방법

에디터에서 **Manage → Library Management**를 열고, **Add Library**를 클릭한 후 다음 주소를 붙여넣습니다:

```text
https://github.com/griptape-ai/griptape-nodes-library-diffusers
```

모달의 **Advanced Options**를 사용하여 브랜치, 태그 또는 커밋을 고정할 수 있습니다. 또는 CLI를 통해 설치할 수도 있습니다:

```bash
gtn libraries download https://github.com/griptape-ai/griptape-nodes-library-diffusers
```

일반적인 설치, 업데이트 및 문제 해결 도움말은 [라이브러리 가이드](../../guides/libraries.md)를 참조하세요.

!!! note "모델 다운로드"

    모든 모델은 처음 사용될 때 로컬 Hugging Face 캐시로 다운로드됩니다(기본 경로: Linux/macOS는 `~/.cache/huggingface/hub`, Windows는 `%USERPROFILE%\.cache\huggingface\hub`). 다른 위치에 저장하려면 엔진을 실행하기 전에 `HF_HOME` 환경 변수를 설정하세요. 계정 및 토큰 설정에 대한 자세한 내용은 [Hugging Face 모델](../../guides/integrations/hugging_face.md)을 참조하세요.

## 작동 원리

일반적인 흐름은 다음과 같습니다:

1. [Pipeline Builder](pipeline_builder.md)로 **파이프라인을 한 번 구축**하고 여러 생성 작업에 걸쳐 재사용합니다.
1. **잠재(latent) 텐서를 생성하거나 로드**합니다(노이즈, 빈(empty) 텐서, 인코딩된 이미지/비디오, 또는 저장된 텐서).
1. [Generate Media Latents](generate_media_latents.md)로 **디퓨전을 실행**하여 새로운 잠재 텐서를 생성합니다 — 다단계(multi-stage) 또는 재디퓨전(rediffusion) 워크플로우를 위해 선택적으로 여러 번 실행할 수 있습니다.
1. 단계 사이에서 수학 연산, 마스크 합성(masked compositing), 또는 업샘플링을 통해 **잠재 텐서를 변환**합니다.
1. [Decode Media Latent](decode_media_latent.md)를 사용하여 최종 잠재 텐서를 다시 이미지나 비디오로 **디코딩**합니다.

모든 단계가 노드로 구성되어 있으므로 단계를 분기, 연결 및 재정렬할 수 있습니다. 이를 통해 단일 엔드투엔드(end-to-end) 생성 노드로는 불가능했던 다단계 미세 조정(multi-stage refinement), ControlNet 중첩(stacking), 잠재 합성, 첫/마지막 프레임 비디오 조건화(first/last-frame video conditioning), 잠재 업스케일링과 같은 고급 패턴을 손쉽게 구현할 수 있습니다.

## 지원되는 모델

모델은 Pipeline Builder에서 `provider` 드롭다운을 통해 선택됩니다. 현재 지원되는 모델 목록:

- **Flux** 및 **Flux2** (Flux2-Klein 포함)
- **Stable Diffusion XL**
- **Qwen-Image** (및 Qwen-Edit)
- **Z-Image**
- **LTX** (비디오)
- **LTX-2.x** (텍스트/이미지/비디오 투 비디오, 이미지 및 비디오 조건화, IC-LoRA, 선형 HDR 출력을 위한 HDR IC-LoRA 지원)
- **WAN** (텍스트 투 비디오 및 이미지 투 비디오)

모델은 Hugging Face 리포지토리에서 Diffusers 형식으로 로드됩니다(단일 파일 `.safetensors` 체크포인트는 직접 로드되지 않으며, Hugging Face repo ID를 사용해야 합니다). 빌더를 통해 파이프라인에 여러 개의 **LoRA**를 연결할 수 있습니다.

## 노드 참조

노드 그룹은 노드 선택기(node picker)의 카테고리를 반영합니다.

### Pipeline

- [Modular Diffusion Pipeline Builder](pipeline_builder.md)
- [ControlNet Pipeline](controlnet_pipeline.md)
- [Load LoRA](load_lora.md)
- [LoRA Pipeline](lora_pipeline.md)

### Create

- [Create Noise Latents](create_noise_latents.md)
- [Create Empty Latents](empty_latents.md)

### Processing

- [Generate Media Latents](generate_media_latents.md)
- [Latent Upsampler](latent_upsampler.md)

### Transform

- [Add Latents](add_latents.md)
- [Subtract Latents](subtract_latents.md)
- [Multiply Latents](multiply_latents.md)
- [Latents Composite Mask](latents_composite_mask.md)

### Conditioning

- [Configure ControlNet](configure_controlnet.md)
- [Media Generation Conditioning](media_gen_conditioning.md)

### Encode / Decode

- [Encode Media Latent](encode_media_latent.md)
- [Encode Masked Media Latent](encode_masked_media_latent.md)
- [Decode Media Latent](decode_media_latent.md)
- [Decode HDR Latents](decode_hdr_latents.md)

### IO

- [Save Latent Tensor](save_latent_tensor.md)

## 실시간 미리보기

생성 중에 중간 디코딩 이미지를 스트리밍하도록 실시간 이미지 미리보기를 활성화할 수 있습니다. 추론 속도는 다소 저하되지만 긴 생성 과정을 모니터링하는 데 유용합니다.

1. 에디터에서 **Settings → Library Settings**를 엽니다.
1. **Modular Diffusion Library** 섹션으로 스크롤합니다.
1. **Enable Image Preview Intermediates**를 켭니다.

## 성능 및 메모리 관리

Pipeline Builder는 로드된 파이프라인을 메모리에 캐시하고 여러 번의 실행에 걸쳐 재사용하며, 설정(구성)이 변경될 때만 파이프라인을 다시 빌드합니다.

VRAM이 적은 환경을 위해 빌더는 **Memory Optimization Strategy** 선택기를 제공합니다:

- **Automatic** — Griptape가 선택된 모델에 적합한 합리적인 기본값을 자동으로 지정합니다.
- **Manual** — 각 옵션을 개별적으로 제어할 수 있습니다:
    - **Quantization mode**: `fp8`, `int8` 또는 `int4` (`optimum-quanto` / `bitsandbytes` 사용) — 약간의 품질 저하를 대가로 트랜스포머 가중치 크기를 줄입니다.
    - **CPU offload strategy**: `Model`(전체 하위 모듈 단위) 또는 `Sequential`(레이어 단위) — 유휴 상태일 때 가중치를 CPU로 이동하여 VRAM을 확보하지만 추론 속도가 느려집니다.
    - **Attention slicing** — 어텐션 연산을 더 작은 청크 단위로 실행합니다. 적은 속도 저하로 손쉽게 메모리를 절약할 수 있습니다.
    - **VAE slicing** — 1개 단위의 배치로 잠재 텐서를 디코딩합니다. 큰 배치 크기를 처리할 때 유용합니다.
    - **Transformer layerwise casting** — 트랜스포머를 더 낮은 정밀도로 유지하고 계산 중에 레이어별로 업캐스팅합니다.

필요한 옵션만 활성화하세요. 각 옵션은 메모리 절약을 위해 어느 정도 속도를 희생합니다. Pipeline Builder에는 자세한 정보가 포함된 파라미터별 도움말 배지가 있습니다.

!!! warning "Advanced Media Library와 함께 사용하는 경우"

    Diffusers Library와 [Advanced Media Library](../../nodes/advanced_media_library/diffusion_pipelines.md)는 여러 업스트림 종속성(예: `diffusers`, `transformers`, `torch`)을 공유하며 각각 자체 인메모리 파이프라인 캐시를 유지합니다. 두 라이브러리를 동일한 세션에서 동시에 로드하여 사용하는 경우, 중복되는 모델 가중치 복사본이 2개씩 VRAM/RAM에 유지되어 메모리 부족(OOM) 오류가 발생할 수 있습니다. 세션당 하나의 라이브러리만 사용하거나 위의 최적화 설정을 통해 메모리 부담을 줄이는 것을 권장합니다.

## 포함된 워크플로우 템플릿

- Text2Image
- MultistageText2Image
- LoRAText2Image
- ControlnetText2Image
- Image2Image
- FirstAndLastFrameImage2Video
- LTX23-HDR-Text2Video-Upsample-Two-Stage

## 지원 및 문의

버그를 발견했거나 기능 요청이 있으신가요?
[이슈 등록(Open an issue)](https://github.com/griptape-ai/griptape-nodes-library-diffusers/issues)을 통해 알려주세요.

