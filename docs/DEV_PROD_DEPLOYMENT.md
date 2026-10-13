# Triển khai dev/prod theo namespace

ThingsBoard triển khai bằng Helm; frontend/backend CD bằng ArgoCD qua Devtron.
GitHub Actions thực hiện CI. Chạy các lệnh trong tài liệu trực tiếp tại root repo,
không cần lưu hoặc gọi file hỗ trợ bên ngoài.
Khong can repo GitOps moi. Hai moi truong dung cung nhanh `main`, values rieng:

| Ung dung | Chart | Dev values | Prod values |
| --- | --- | --- | --- |
| ThingsBoard | `helm/thingsboard` | `environments/dev/values.yaml` | `environments/prod/values.yaml` |
| FE | `helm/hcm-flood-frontend` | `environments/dev/values.yaml` | `environments/prod/values.yaml` |
| BE | `helm/hcm-flood-backend` | `environments/dev/values.yaml` | `environments/prod/values.yaml` |

Dev namespace: `iot-dev`; prod du kien: `iot-prod`. Khong tu dong di chuyen prod hien tai.
Values prod la cau hinh dich; chi chuyen Application prod sang file nay sau khi chot
namespace, endpoints, secrets va image dang chay. ThingsBoard prod van bat cac
thanh phan phu/Kafka theo chart cu; day khong phai de xuat thay doi topology prod.

## Dieu kien truoc khi deploy dev

- Tao PostgreSQL database/user RIENG cho dev tren CMC Cloud; DB phai rong neu bootstrap.
- Tao Redis RIENG cho dev. Khong dung chung instance prod chi bang cach doi `REDIS_DB`.
- Cho phep ket noi tu workload cluster toi CMC PostgreSQL/Redis, DNS va cac API ngoai cua BE.
- ArgoCD da cai tren CUNG cluster dich va da co quyen doc repo GitHub nay.
- Xac nhan namespace ArgoCD (co the la `argocd` hoac `devtroncd`) va Argo Project.
- Nodes can co label `nodegroup=workload`, hoac doi `nodeSelector` trong values dev.
- Dev domains mac dinh: `flood.dev.web-ui.com`, `thingsboard.dev.web-ui.com`.
  Doi sang domain thuc te va tro DNS toi ingress-nginx.
- Image ThingsBoard duoc giu o `3.4.0`, dung voi chart hien tai. Manifest AWS trong repo
  dung version khac; khong ket noi image 3.4.0 vao DB cua version moi hon.
- FE/BE dev ban dau dung SHA tag hien co; sau commit nay, CI build se ghi digest moi.
  Doi CI xong va ArgoCD sync digest truoc khi kiem thu/promote.
- Neu image GHCR private, tao pull Secret trong `iot-dev` va dien `imagePullSecrets`
  cho FE/BE. Cac lenh ben duoi khong tao registry credentials.

## Commit/push (PowerShell)

Chon rieng cac duong dan ben duoi; khong gom cac thay doi xoa chart portal da co san.
Nếu cần commit việc xóa chart portal hoặc workflow simulator, stage riêng các thay đổi đó.

```powershell
git diff --check
git add -- .github/workflows/frontend-ci.yml .github/workflows/backend-ci.yml backend/app/services/thingsboard_service.py helm/thingsboard helm/hcm-flood-frontend helm/hcm-flood-backend docs/DEV_PROD_DEPLOYMENT.md
git diff --cached --stat
git commit -m "feat: add namespace-based dev/prod deployments and immutable image promotion"
git push origin HEAD
```

## Branch source va trigger CI

Devtron chi quan ly CD qua ArgoCD; GitHub Actions quan ly CI.
Push code FE/BE len branch `dev` trigger workflow tuong ung theo path filter.
Workflow build tu source `dev`, sau do checkout RIENG `main` vao `deployment-config`
va cap nhat truc tiep image.tag/digest trong values dev ngay trong workflow YAML.
Khong can file script update image va khong merge source dev vao main khi ghi values.
Push source len `main` khong trigger build FE/BE. workflow_dispatch chi build khi chon `dev`.
ArgoCD dev/prod van doc values tren `main`, khong dung branch moi truong rieng cho manifests.

Commit cau hinh nay vao `main` de ArgoCD doc chart/values, va dua workflow vao `dev`
qua PR/merge theo quy trinh repo. Neu branch `dev` chua ton tai, sau khi `main` co
cau hinh moi co the tao bang `git switch -c dev origin/main`, roi `git push -u origin dev`.
Neu `dev` da ton tai, merge cau hinh vao branch do; khong reset/force-push branch.
Sau do push thay doi FE/BE len `dev` (hoac chon Run workflow -> branch dev).
Khong chi push workflow len main roi cho CI build: workflow phai co tren dev.
Truoc khi deploy, ArgoCD dev theo doi `main` va chart/values moi phai co tren main.
Repo phai cho phep GitHub Actions ghi contents. Neu `main` duoc bao ve cam bot push,
can doi buoc cap nhat dev sang tao PR, khong tat bao ve prod de giai quyet.

## 1. Khai báo biến CMC Cloud và kiểm tra đầu vào

Chạy tất cả block trong cùng một phiên PowerShell tại root repo. Helm không tự
nội suy biến PowerShell trong YAML. Lệnh ở bước 2 gửi trực tiếp các biến thành
Secret qua stdin, không ghi password vào file Git. TLS/sslmode phải khớp dịch vụ CMC.
Nếu cần CA riêng, mount CA và cấu hình trust trước khi chạy.

```powershell
$ErrorActionPreference = 'Stop'
$DEV_KUBE_CONTEXT = '<context-cluster-CMC>'
$DEV_ARGO_NAMESPACE = 'argocd' # Hoặc devtroncd: chọn namespace ArgoCD thực tế
$DEV_ARGO_PROJECT = 'default'
$DEV_REPO_URL = 'https://github.com/tranduyloc895/iot-thingsboard.git'
$namespace = 'iot-dev'

$env:DEV_PG_HOST = '<endpoint-PostgreSQL-dev-CMC>'
$env:DEV_PG_PORT = '5432'
$env:DEV_PG_DATABASE = 'thingsboard_dev'
$env:DEV_PG_USERNAME = 'thingsboard_dev'
$env:DEV_PG_PASSWORD = [System.Net.NetworkCredential]::new('', (Read-Host 'PostgreSQL dev password' -AsSecureString)).Password
$env:DEV_PG_SSLMODE = 'require' # Điều chỉnh theo CMC

$env:DEV_REDIS_HOST = '<endpoint-Redis-dev-CMC>'
$env:DEV_REDIS_PORT = '6379'
$env:DEV_REDIS_DB = '0'
$env:DEV_REDIS_PASSWORD = [System.Net.NetworkCredential]::new('', (Read-Host 'Redis dev password' -AsSecureString)).Password
$env:DEV_REDIS_TLS_ENABLED = 'false' # true nếu CMC bật TLS

$env:DEV_TB_USERNAME = 'tenant@thingsboard.org'
$env:DEV_TB_PASSWORD = 'tenant' # Chỉ tenant demo lần bootstrap; đổi ngay sau đó

if ($DEV_KUBE_CONTEXT -like '<*' -or $env:DEV_PG_HOST -like '<*' -or $env:DEV_REDIS_HOST -like '<*') {
    throw 'Replace CMC endpoints and kube context before deploying'
}
function Invoke-Kube {
    & kubectl --context $DEV_KUBE_CONTEXT @args
    if ($LASTEXITCODE -ne 0) { throw "kubectl failed (exit $LASTEXITCODE)" }
}

function Apply-Object($Object) {
    $Object | ConvertTo-Json -Depth 30 | & kubectl --context $DEV_KUBE_CONTEXT apply -f -
    if ($LASTEXITCODE -ne 0) { throw 'kubectl apply failed' }
}

function Required-Env([string]$Name) {
    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) { throw "Set `$env:$Name before running this script" }
    return $value
}

# Validate all settings before changing the cluster.
$pgHost = Required-Env 'DEV_PG_HOST'
$pgPort = Required-Env 'DEV_PG_PORT'
$pgDatabase = Required-Env 'DEV_PG_DATABASE'
$pgUsername = Required-Env 'DEV_PG_USERNAME'
$pgPassword = Required-Env 'DEV_PG_PASSWORD'
$pgSslMode = Required-Env 'DEV_PG_SSLMODE'
$redisHost = Required-Env 'DEV_REDIS_HOST'
$redisPort = Required-Env 'DEV_REDIS_PORT'
$redisDatabase = Required-Env 'DEV_REDIS_DB'
$redisPassword = [Environment]::GetEnvironmentVariable('DEV_REDIS_PASSWORD')
if ($null -eq $redisPassword) { $redisPassword = '' }
$redisTls = Required-Env 'DEV_REDIS_TLS_ENABLED'
$tbUsername = Required-Env 'DEV_TB_USERNAME'
$tbPassword = Required-Env 'DEV_TB_PASSWORD'
if ($pgSslMode -notin @('disable','allow','prefer','require','verify-ca','verify-full')) { throw 'Invalid DEV_PG_SSLMODE' }
if ($redisTls -notin @('true','false')) { throw 'DEV_REDIS_TLS_ENABLED must be true or false' }
foreach ($port in @($pgPort, $redisPort)) {
    if ($port -notmatch '^\d+$' -or [int]$port -lt 1 -or [int]$port -gt 65535) { throw 'Invalid database/Redis port' }
}
if ($pgDatabase -notmatch '^[A-Za-z0-9_-]+$') { throw 'Use a simple PostgreSQL database name' }
if ($redisDatabase -notmatch '^\d+$') { throw 'Invalid Redis database index' }

```

## 2. Tạo namespace và ba Secret

Có thể chạy lại bước 1–2 khi cập nhật credentials. Redis password có thể rỗng nếu
CMC không bật authentication. Secret thay đổi không tự cập nhật env của pod:
restart ThingsBoard và BE sau khi các Deployment đã tồn tại.

```powershell
Apply-Object @{ apiVersion='v1'; kind='Namespace'; metadata=@{name=$namespace} }
Apply-Object @{
    apiVersion='v1'; kind='Secret'; metadata=@{name='thingsboard-postgresql'; namespace=$namespace}; type='Opaque'
    stringData=@{
        SPRING_DATASOURCE_URL="jdbc:postgresql://${pgHost}:${pgPort}/${pgDatabase}?sslmode=${pgSslMode}"
        SPRING_DATASOURCE_USERNAME=$pgUsername; SPRING_DATASOURCE_PASSWORD=$pgPassword
    }
}
Apply-Object @{
    apiVersion='v1'; kind='Secret'; metadata=@{name='thingsboard-redis'; namespace=$namespace}; type='Opaque'
    stringData=@{
        REDIS_HOST=$redisHost; REDIS_PORT=$redisPort; REDIS_DB=$redisDatabase
        REDIS_PASSWORD=$redisPassword; TB_REDIS_SSL_ENABLED=$redisTls
    }
}
Apply-Object @{
    apiVersion='v1'; kind='Secret'; metadata=@{name='thingsboard-api-credentials'; namespace=$namespace}; type='Opaque'
    stringData=@{THINGSBOARD_USERNAME=$tbUsername; THINGSBOARD_PASSWORD=$tbPassword}
}

```

## 3. Triển khai ThingsBoard bằng Helm

**Chỉ lần đầu**, khi PostgreSQL DB dev rỗng và Helm release chưa tồn tại.
`helm install` sẽ từ chối nếu release đã tồn tại. Hook post-install chạy init DB;
không thêm `--wait` vào bước bootstrap vì node cần schema do hook tạo.
Load demo tạo tenant `tenant@thingsboard.org`, password ban đầu `tenant`.

```powershell
helm install thingsboard helm/thingsboard `
  --kube-context $DEV_KUBE_CONTEXT --namespace $namespace `
  -f helm/thingsboard/environments/dev/values.yaml `
  --set node.initDb=true --set node.loadDemo=true --timeout 20m
if ($LASTEXITCODE -ne 0) { throw 'Bootstrap failed; inspect init job before continuing' }
```

Sau bootstrap, chạy lệnh dưới để tắt init trong release và chờ ThingsBoard ready.
Cũng dùng lệnh này cho **các lần cập nhật sau**, không chạy lại demo init.

```powershell
helm upgrade --install thingsboard helm/thingsboard `
  --kube-context $DEV_KUBE_CONTEXT --namespace $namespace `
  -f helm/thingsboard/environments/dev/values.yaml `
  --set node.initDb=false --wait --timeout 20m
if ($LASTEXITCODE -ne 0) { throw 'ThingsBoard deployment failed' }

# Nạp lại endpoint/credentials nếu vừa thay đổi Secret.
Invoke-Kube -n $namespace rollout restart deployment/thingsboard-node
Invoke-Kube -n $namespace rollout status deployment/thingsboard-node --timeout=15m
```

Đổi mật khẩu tenant qua ThingsBoard UI ngay sau bootstrap, rồi cập nhật Secret BE:

```powershell
$env:DEV_TB_PASSWORD = [System.Net.NetworkCredential]::new('', (Read-Host 'New ThingsBoard tenant password' -AsSecureString)).Password
Apply-Object @{
    apiVersion='v1'; kind='Secret'; metadata=@{name='thingsboard-api-credentials'; namespace=$namespace}; type='Opaque'
    stringData=@{THINGSBOARD_USERNAME=$env:DEV_TB_USERNAME; THINGSBOARD_PASSWORD=$env:DEV_TB_PASSWORD}
}
# Restart BE sau khi Deployment đã được ArgoCD tạo ở bước 4.
```

## 4. Tạo hai Application ArgoCD dev

Commit chart/values lên main trước. ArgoCD phải có quyền đọc repo và AppProject
cho phép source repo/namespace đích. Release name BE giữ `hcm-flood-backend` để
khớp Nginx FE. Không cài FE/BE bằng Helm CLI song song với ArgoCD.

```powershell
foreach ($component in @('frontend','backend')) {
    Apply-Object @{
        apiVersion='argoproj.io/v1alpha1'; kind='Application'
        metadata=@{name="hcm-flood-${component}-dev"; namespace=$DEV_ARGO_NAMESPACE}
        spec=@{
            project=$DEV_ARGO_PROJECT
            source=@{
                repoURL=$DEV_REPO_URL; targetRevision='main'; path="helm/hcm-flood-${component}"
                helm=@{releaseName="hcm-flood-${component}"; valueFiles=@('environments/dev/values.yaml')}
            }
            destination=@{server='https://kubernetes.default.svc'; namespace=$namespace}
            syncPolicy=@{automated=@{prune=$true; selfHeal=$true}; syncOptions=@('CreateNamespace=true')}
        }
    }
}
Invoke-Kube -n $DEV_ARGO_NAMESPACE get applications
Invoke-Kube -n $namespace get pods,svc,ingress
```

Destination mặc định là cluster nội bộ `https://kubernetes.default.svc`.
Nếu ArgoCD ở cluster khác, đổi server sang cluster đích đã đăng ký.
ArgoCD sync bất đồng bộ; chờ nó tạo Deployment trước khi chạy rollout status.
Nếu BE đã tồn tại và vừa đổi Secret, nạp lại credentials:

```powershell
Invoke-Kube -n $namespace rollout restart deployment/hcm-flood-backend
```

Dev có ba pod ứng dụng thường trực: ThingsBoard mono, FE và BE; không có HPA hoặc
pod Kafka/Zookeeper/transport/web-ui/js-executor riêng/Redis/PostgreSQL.
DB và Redis ở CMC. Queue in-memory dev mất hàng đợi khi restart. Job bootstrap
và pod tạm lúc rolling update không tính vào ba pod thường trực.
MQTT 1883 chỉ là ClusterIP; từ ngoài cluster cần LoadBalancer/TCP ingress riêng.
HTTP/UI/API ThingsBoard được route thẳng tới mono node.

## 5. Kiểm thử dev trước merge PR prod

Chạy trong cùng phiên đã khai báo biến/hàm ở bước 1. Chờ ArgoCD Synced/Healthy và
CI pin image bằng digest. Ghi lại revision/image trước và sau kiểm thử; nếu dev
đổi trong lúc kiểm thử, các lệnh dưới từ chối kết quả và yêu cầu kiểm thử lại.

```powershell
$ErrorActionPreference = 'Stop'
function Get-DevSnapshot {
    $snapshot = @{}
    foreach ($component in @('frontend','backend')) {
        $raw = & kubectl --context $DEV_KUBE_CONTEXT -n $DEV_ARGO_NAMESPACE get application "hcm-flood-${component}-dev" -o json
        if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect ArgoCD dev revision' }
        $app = $raw | ConvertFrom-Json
        if ($app.status.sync.status -ne 'Synced' -or $app.status.health.status -ne 'Healthy') { throw "$component dev is not Synced/Healthy" }
        $raw = & kubectl --context $DEV_KUBE_CONTEXT -n iot-dev get deployment "hcm-flood-$component" -o json
        if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect dev image' }
        $deployment = $raw | ConvertFrom-Json
        $image = $deployment.spec.template.spec.containers[0].image
        if ($image -notmatch '@sha256:[0-9a-f]{64}$') { throw 'Wait for CI to pin dev images by digest before testing for promotion' }
        $snapshot[$component] = @{revision=$app.status.sync.revision; image=$image}
    }
    if ($snapshot.frontend.revision -ne $snapshot.backend.revision) { throw 'Wait until both dev applications are synced to the same Git revision' }
    return $snapshot
}
foreach ($name in @('thingsboard-node','hcm-flood-frontend','hcm-flood-backend')) {
    & kubectl --context $DEV_KUBE_CONTEXT -n iot-dev rollout status "deployment/$name" --timeout=15m
    if ($LASTEXITCODE -ne 0) { throw "Deployment $name is not ready" }
}
$before = Get-DevSnapshot

# Runs inside BE with its own Secret/config. No credentials are printed.
$check = @'
import json, os, urllib.request
def get(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        assert response.status == 200
        return response.read()
assert json.loads(get('http://127.0.0.1:8000/healthz'))['env'] == 'development'
assert b'<html' in get('http://hcm-flood-frontend/').lower()
base = os.environ['THINGSBOARD_URL'].rstrip('/')
assert '.iot-dev.svc.cluster.local' in base
payload = json.dumps({'username':os.environ['THINGSBOARD_USERNAME'], 'password':os.environ['THINGSBOARD_PASSWORD']}).encode()
request = urllib.request.Request(base+'/api/auth/login', data=payload, headers={'Content-Type':'application/json'})
with urllib.request.urlopen(request, timeout=30) as response:
    token = json.load(response)['token']
request = urllib.request.Request(base+'/api/tenant/devices?pageSize=1&page=0', headers={'X-Authorization':'Bearer '+token})
with urllib.request.urlopen(request, timeout=30) as response:
    assert response.status == 200
get('http://127.0.0.1:8000/api/v1/dashboard')
print('PASS: BE, FE, dev ThingsBoard tenant login/API and dashboard')
'@
$check | & kubectl --context $DEV_KUBE_CONTEXT -n iot-dev exec -i deployment/hcm-flood-backend -- python -
if ($LASTEXITCODE -ne 0) { throw 'Dev smoke test failed' }
$after = Get-DevSnapshot
foreach ($component in @('frontend','backend')) {
    if ($before[$component].revision -ne $after[$component].revision -or $before[$component].image -ne $after[$component].image) {
        throw 'Dev changed during testing; rerun the test on a stable revision'
    }
    Write-Host "$component verified image: $($after[$component].image)"
}
Write-Host "Tested dev revision: $($after.frontend.revision)"
Write-Host 'Also verify browser WebSocket/live telemetry and record both image digests before promotion.'
```

Kiểm tra thêm WebSocket, telemetry/device thật và nghiệp vụ bằng trình duyệt.
Dashboard có fallback nên HTTP 200 không đủ chứng minh telemetry thật hoạt động.
So sánh digest đã kiểm thử với digest trong PR; ghi revision, cả hai image và kết
quả kiểm thử vào PR trước merge. Nếu dev đã chạy image khác, kiểm thử đó không
xác nhận ứng viên cũ trong PR.

## PR promote tu dong sau moi build dev

Luồng chính đã được cấu hình trong workflow FE/BE:

```text
Push source lên dev → GitHub Actions build/push GHCR
  → commit image.tag/digest vào values dev trên main
  → ArgoCD dev sync
  → CI mở PR promote vào main (chỉ values prod)
  → kiểm thử đúng image ở dev, ghi kết quả vào PR
  → người dùng duyệt và MERGE PR
  → values prod trên main thay đổi → ArgoCD prod sync
```

CI mở PR sau khi cập nhật desired state dev; không đợi ArgoCD rollout hay chạy test
cluster. Kiểm thử dev là bước thủ công trước merge, bằng các lệnh ở bước 5 và kiểm thử
WebSocket/telemetry/nghiệp vụ. Không merge chỉ vì image build thành công.

Mỗi component/build có PR riêng và nhánh `codex/promote-<component>-<run-id>-<attempt>`.
PR giữ nguyên digest build của lần chạy đó, chứa source SHA, commit cấu hình dev và
link CI. Build dev mới không ghi đè PR cũ. Nếu cả FE/BE thay đổi sẽ có hai PR; kiểm
thử đúng cặp image và merge các PR tương ứng. Đóng PR cũ đã bị bản mới thay thế.
Không merge lại PR cũ sau khi đã promote bản mới hơn.

PR chỉ thay `image.tag` và `image.digest` của component trong values prod.
Không merge source branch dev vào main để promote, không build lại khi merge.
Bấm **Approve** chưa đổi prod; phải bấm **Merge pull request** mới kích hoạt sync.
Không cấu hình auto-merge cho các PR promotion.

### Thiết lập GitHub và ArgoCD cần làm một lần

- GitHub repo → Settings → Actions → General → Workflow permissions:
  cho phép read/write và bật **Allow GitHub Actions to create and approve pull requests**.
  Workflow chỉ tạo PR, không tự approve/merge. Policy organization có thể chặn quyền này.
- Workflow khai báo `contents: write`, `packages: write`, `pull-requests: write`.
- CI phải được phép commit **values dev** lên main. Nếu main yêu cầu mọi thay đổi đều
  qua PR và không cho bot push, bước cập nhật dev sẽ bị từ chối. Cần thống nhất chính
  sách bot với admin, hoặc đổi riêng bước dev thành PR được duyệt/merge; không tự bỏ
  branch protection để chạy pipeline.
- Quy định người dùng review/test trước merge PR promotion. Quy trình này chưa có test
  gate tự động từ cluster; muốn enforce cần CI runner có kết nối CMC/ArgoCD.
- FE/BE ArgoCD prod: branch `main`, chart tương ứng, `helm.valueFiles` chọn
  `environments/prod/values.yaml`, namespace prod, bật auto-sync. Xóa các image overrides
  trong `parameters`, `values`, `valuesObject` nếu chúng đang ghi đè image từ file prod.
- Config/secrets/domain/database prod phải được chuẩn bị riêng trước khi đổi Application
  prod sang values mới. Việc tạo PR không tự cấu hình Application prod hiện hữu.

Theo [GitHub GITHUB_TOKEN docs](https://docs.github.com/en/actions/concepts/security/github_token),
PR do `GITHUB_TOKEN` tạo/cập nhật có thể khởi tạo workflow ở trạng thái cần người dùng
approve để chạy. Nếu có required PR checks, kiểm tra banner **Approve workflows to run**;
không giả định checks tự chạy mà không có phê duyệt. Dùng GitHub App token nếu cần
chạy tự động theo chính sách repo. Các push do GITHUB_TOKEN không trigger CI push khác.

Chart/templates dung chung van co the tac dong prod khi commit tren `main`, ke ca
khong doi image. Trong giai doan chuyen doi, pin revision Argo prod vao commit dang
chay da xac nhan; chi cap nhat sau review. Ve sau, PR thay doi chart/template can
review va kiem thu nhu thay doi prod. Chi sua values dev khong doi manifest prod
khi prod da khai bao image/config rieng.

Prod can Secret rieng trong namespace prod: `thingsboard-postgresql`,
`thingsboard-redis`, `thingsboard-api-credentials`. Khong copy Secret hoac DB dev.
Khoi tao/upgrade schema ThingsBoard la thao tac rieng, khong chay lai demo init tren prod.
