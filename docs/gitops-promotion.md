# Multi-environment GitOps: code dev, configuration main

## Mô hình đang dùng

Hai môi trường Devtron cùng đọc nhánh `main` là phù hợp. **Nhánh chứa source để
build** và **nhánh chứa cấu hình triển khai** không cần giống nhau. Hai môi trường
được phân biệt bằng values file và namespace, không bắt buộc bằng nhánh Git.

| Vai trò | Nhánh | File/đối tượng |
| --- | --- | --- |
| Source CI build | `dev` | `frontend/`, `backend/` |
| Cấu hình triển khai dev | `main` | `helm/hcm-flood-<component>/environments/dev/values.yaml` |
| Cấu hình triển khai prod | `main` | `helm/hcm-flood-<component>/environments/prod/values.yaml` |

Không cần push source thẳng lên main để deploy dev. Image được build từ source
SHA trên dev và lưu ở GHCR; Devtron triển khai image theo digest trong values.
Việc merge source code vào main để quản lý release có thể qua PR riêng. PR
promote image chỉ cập nhật cấu hình image, không tự merge source hoặc chart.

## Quy trình tự động

1. Push code lên **dev**. CI của component chạy security, build image một lần,
   gắn tag source SHA, scan image, rồi push GHCR. Demo `report-only` vẫn giữ
   report; lỗi build/push/Git vẫn làm CI fail.
2. Bot checkout **main**, chỉ sửa `image.tag`/`image.digest` trong **dev values**,
   rồi commit/push **HEAD:main**. Prod values giữ nguyên. `[skip ci]` và filter
   nhánh/path tránh build lặp. FE/BE rebase/retry khi cùng cập nhật main.
3. Devtron dev đọc **main + dev values** và triển khai theo cấu hình sync của
   môi trường. Bạn kiểm thử đúng digest này tại dev.
4. Bot tạo nhánh `codex/promote-<component>-<run>-<attempt>` từ **origin/main**,
   xác nhận tag/digest trong snapshot dev values của main, chỉ sửa **prod values**,
   rồi mở PR vào main. PR ghi source SHA, dev configuration SHA, image digest,
   chế độ security và link CI. Không rebuild image.
5. Bạn xem report và test dev, vào PR → Files changed → kiểm tra chỉ tag/digest
   production thay đổi → Review changes → **Approve**. Approve chưa merge.
6. Bạn nhấn **Merge pull request → Confirm merge**. Khi đó **prod values trên main**
   mới đổi. Devtron prod đọc main + prod values và triển khai theo chế độ sync
   đang cấu hình. Bot không approve hoặc tự merge PR.

**Không cần commit tay để promote**: bot đã chuẩn bị commit/PR; bạn chỉ duyệt và
merge. Trước khi merge PR, main có thể đã nhận dev image, nhưng prod image vẫn
chưa đổi. Đây là khác biệt giữa nhánh main và môi trường production.

Mỗi build có ứng viên/PR riêng. Build sau không tự thay digest trong PR trước;
chọn đúng PR đã kiểm thử, tránh merge PR cũ sau khi đã promote bản mới. Các PR cũ
được tạo khi workflow ghi dev values trên nhánh dev không chứng minh image đã
được triển khai bởi Devtron theo main; nên dùng ứng viên mới sau sửa luồng.

## Cấu hình Devtron

Giữ cả hai môi trường theo dõi main, với cấu hình tách riêng:

| Môi trường | Revision | Chart path | Values file | Namespace |
| --- | --- | --- | --- | --- |
| Dev | `main` | `helm/hcm-flood-backend` hoặc `helm/hcm-flood-frontend` | `environments/dev/values.yaml` | `iot-dev` |
| Prod | `main` | chart tương ứng | `environments/prod/values.yaml` | `iot-prod` |

Không để cả hai môi trường dùng chung dev values. Kiểm tra các image override
trong Devtron hoặc Helm parameters/inline values không ghi đè digest trong file.
Repo chưa chứa Application/ApplicationSet đang chạy nên pipeline không tự đổi
cấu hình Devtron/cluster và không tự chứng minh rollout thành công. Nếu bật auto
sync, merge prod PR là thao tác kích hoạt production; nếu sync thủ công thì cần
thêm thao tác deploy/sync trên Devtron sau merge.

## Approval và quyền GitHub

- Cho phép Actions tạo PR trong Settings → Actions → General → Workflow permissions.
  Workflow có quyền write để push dev values lên main và mở PR; không có lệnh
  `gh pr review` hoặc `gh pr merge`.
- `SECURITY_GATE_MODE=report-only` cho demo; đổi thành `enforce` để security chặn
  lại. Xem [security pipeline](security-pipeline.md).
- Khi kiểm tra ngày 15/10/2026, GitHub API báo branch protection cho repo private
  này cần gói cao hơn. Hiện không thể bắt buộc mọi người dùng phải review trước
  merge chỉ bằng workflow. Pipeline chỉ tự động thay dev values; prod values
  được đưa qua PR.
- Khi bổ sung branch protection, lưu ý bot vẫn cần ghi dev values vào main.
  Quyền bypass của bot là quyền nhạy cảm; PR-only cho mọi thay đổi sẽ yêu cầu cả
  cập nhật dev qua PR hoặc dùng kiến trúc GitOps khác. Không giả định quyền bypass
  phân biệt được dev/prod theo file path.

Ở quy mô lớn hơn, có thể tách source và GitOps thành hai repository: source dùng
feature/dev/main theo quy trình phát triển; GitOps dùng một nhánh main với thư mục
mỗi môi trường. Mô hình hiện tại giữ cùng repo để demo, nhưng vẫn tách rõ hai vai
trò và promote đúng image digest.

## Kiểm chứng và rollback

- CI push main: diff chỉ có dev values của component tương ứng, prod giữ nguyên.
- PR promotion: diff chỉ có prod values, digest khớp snapshot dev ghi trong PR.
- Test dev trên Devtron trước khi merge; kiểm tra health và digest đang chạy.
- Sau merge, kiểm tra health/digest production theo chính sách sync Devtron.
- Rollback bằng PR revert commit promotion trên main. Sau khi duyệt/merge và sync,
  prod quay về digest cũ. Rollback dev có thể revert riêng commit dev image.

Tích hợp không tự merge PR và không chạy lệnh deploy/sync production.
