import torch

ok = torch.cuda.is_available()
name = torch.cuda.get_device_name(0) if ok else "no cuda device"
print("torch", torch.__version__, "cuda", torch.version.cuda, "device", name)
if ok:
    a = torch.randn(2048, 2048, device="cuda")
    b = a @ a
    torch.cuda.synchronize()
    print("matmul ok", tuple(b.shape))
