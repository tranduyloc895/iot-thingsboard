# Quy trình dev → approve → merge → production

## Luồng sau thay đổi

1. Push code lên **`dev`**. Backend/frontend CI chỉ chạy khi phần code hoặc cấu
   hình pipeline tương ứng thay đổi. Chạy security, build image gắn source commit
   SHA, scan image, rồi push GHCR. Chế độ demo `report-only` vẫn tạo report dù có
   phát hiện bảo mật; lỗi build/push/Git vẫn làm CI fail.
2. Bot checkout **`dev`**, chỉ cập nhật `image.tag` và `image.digest` trong
   `helm/hcm-flood-<component>/environments/dev/values.yaml`, rồi commit/push về
   **`dev`**. Không có lệnh push `HEAD:main`. Bot commit `[skip ci]` và chỉ đổi
   values nên không tạo vòng lặp build. Nếu hai pipeline cập nhật đồng thời,
   mỗi pipeline rebase/retry để giữ thay đổi của component còn lại.
3. ArgoCD dev cần theo dõi `targetRevision: dev`, chart path tương ứng và
   `helm.valueFiles: [environments/dev/values.yaml]`. Khi bật auto-sync, image
   mới được triển khai vào môi trường dev để kiểm thử.
4. Bot tạo nhánh ứng viên riêng `codex/promote-<component>-<run>-<attempt>` từ
   **`origin/main`**. Bot xác nhận đúng tag/digest đã ghi trên dev, chỉ sửa
   `environments/prod/values.yaml`, rồi tạo PR vào **`main`**. Không rebuild;
   source SHA, dev config SHA, digest và link CI được ghi trong PR.
5. Bạn kiểm thử dev, xem artifact HTML, rồi vào PR → **Files changed** để xác
   nhận chỉ có tag/digest production thay đổi. Dùng **Review changes → Approve**.
   Approve chỉ ghi nhận duyệt; nó chưa đưa thay đổi vào `main`.
6. Bạn nhấn **Merge pull request → Confirm merge**. Khi đó `main` mới nhận
   image production. ArgoCD prod theo dõi `targetRevision: main` và
   `helm.valueFiles: [environments/prod/values.yaml]`; auto-sync sẽ triển khai
   đúng digest đã duyệt. Không bật auto-merge, bot không approve hoặc merge PR.

Mỗi ứng viên là một nhánh/PR riêng. Build dev tiếp theo không tự thay image
trong PR cũ. Tránh merge lại một PR cũ sau khi đã promote image mới hơn. PR
promote image không gộp code hoặc chart từ dev; các thay đổi code/chart/workflow
cần PR riêng nếu muốn đưa vào main. Không merge toàn bộ dev vào main chỉ để
promote một image.

## Thiết lập ArgoCD

Repo chưa chứa Application/ApplicationSet đang dùng trên cluster, nên thay đổi
pipeline không tự đổi cấu hình ArgoCD. Cần cấu hình cả frontend và backend:

| Môi trường | Git revision | Chart path | Helm value file | Namespace |
| --- | --- | --- | --- | --- |
| Dev | `dev` | `helm/hcm-flood-backend` hoặc `helm/hcm-flood-frontend` | `environments/dev/values.yaml` | `iot-dev` |
| Production | `main` | chart tương ứng | `environments/prod/values.yaml` | `iot-prod` |

Nếu Application dùng `sources` thay vì `source`, sửa revision đúng Git source.
Kiểm tra `parameters`, `valuesObject` hoặc inline `values` không ghi đè image từ
file môi trường. Nếu dev vẫn theo dõi main thì commit image trên dev chưa thể
được triển khai. Sau khi đổi nguồn, kiểm tra diff và health trước khi sync.

Tài liệu ArgoCD: [Application specification](https://argo-cd.readthedocs.io/en/latest/user-guide/application-specification/),
[Helm values precedence](https://argo-cd.readthedocs.io/en/latest/user-guide/helm/).

## Thiết lập GitHub

- **Settings → Actions → General → Workflow permissions**: cho phép Actions tạo
  PR. Pipeline vẫn dùng `contents: write`, `packages: write`, `pull-requests: write`
  cho job publish. Quyền tạo/approve PR không có nghĩa bot tự approve: workflow
  chỉ gọi `gh pr create`, không có lệnh review hoặc merge.
- **Settings → Secrets and variables → Actions → Variables**:
  `SECURITY_GATE_MODE=report-only` cho demo; đổi thành `enforce` để security chặn
  lại. Workflow mặc định `report-only` nếu chưa tạo biến. Chi tiết tại
  [security pipeline](security-pipeline.md).
- Nếu gói GitHub hỗ trợ, bảo vệ `main`: Require a pull request before merging,
  Required approvals = 1, Dismiss stale approvals, chặn force-push và không cho
  bypass. Có thể yêu cầu check **Source security gate** sau khi workflow đã có
  trên main. Cho phép bot commit image values trên dev.

Khi kiểm tra ngày 15/10/2026, GitHub API trả về **403** cho branch protection:
repo private cần nâng cấp GitHub Pro hoặc chuyển public để dùng tính năng này.
Vì vậy pipeline bảo đảm bot không push trực tiếp vào main, nhưng chưa thể bắt
buộc review đối với mọi người dùng có quyền push. Không thay đổi visibility repo.

PR do `GITHUB_TOKEN` tạo có thể cần bạn approve workflow run trong tab Actions
trước khi check chạy. Đây là approve chạy workflow, khác với approve review PR
và khác với merge. Xem [GitHub workflow triggers](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

## Kiểm chứng và rollback

- Sau lượt CI, kiểm tra commit bot chỉ nằm trên dev và chỉ sửa dev values;
  main phải giữ nguyên SHA trước khi bạn merge.
- Kiểm tra PR promotion chỉ chứa file prod values của component tương ứng;
  tag/digest khớp snapshot dev được dẫn trong PR.
- Sau merge, xác nhận ArgoCD prod Synced/Healthy và pod dùng đúng digest.
- Rollback bằng PR revert commit promotion trên main. Sau khi bạn duyệt/merge,
  ArgoCD trả image về digest trước đó; kiểm tra rollout/health tương tự.

Tích hợp này không tự merge PR, không chạy lệnh deploy production, và không tự
áp dụng hoặc sync Application trên cluster.
