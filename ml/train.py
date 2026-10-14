"""Train a ResNet18 classifier from a torchvision ImageFolder dataset."""
import argparse, json, random
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--data-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,default=Path("backend/models"))
    p.add_argument("--epochs",type=int,default=5)
    p.add_argument("--batch-size",type=int,default=32)
    p.add_argument("--seed",type=int,default=42)
    a=p.parse_args()
    if a.epochs<1 or a.batch_size<1: p.error("epochs and batch-size must be positive")
    random.seed(a.seed);torch.manual_seed(a.seed)
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    norm=transforms.Normalize([.485,.456,.406],[.229,.224,.225])
    train_tf=transforms.Compose([transforms.RandomResizedCrop(224,scale=(.75,1)),transforms.RandomHorizontalFlip(),transforms.RandomRotation(12),transforms.ToTensor(),norm])
    eval_tf=transforms.Compose([transforms.Resize((224,224)),transforms.ToTensor(),norm])
    base=datasets.ImageFolder(a.data_dir)
    if len(base.classes)<2 or len(base)<10: p.error("Need at least two classes and ten images")
    order=list(range(len(base)));random.Random(a.seed).shuffle(order)
    test_n=max(1,int(.15*len(order)));val_n=max(1,int(.15*len(order)));train_n=len(order)-test_n-val_n
    if train_n<1:p.error("Not enough data for three splits")
    train_ds=datasets.ImageFolder(a.data_dir,transform=train_tf)
    eval_ds=datasets.ImageFolder(a.data_dir,transform=eval_tf)
    loaders=[
      DataLoader(Subset(train_ds,order[:train_n]),batch_size=a.batch_size,shuffle=True,num_workers=0),
      DataLoader(Subset(eval_ds,order[train_n:train_n+val_n]),batch_size=a.batch_size,shuffle=False,num_workers=0),
      DataLoader(Subset(eval_ds,order[train_n+val_n:]),batch_size=a.batch_size,shuffle=False,num_workers=0)]
    model=models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc=nn.Linear(model.fc.in_features,len(base.classes));model.to(device)
    opt=torch.optim.AdamW(model.parameters(),lr=2e-4);loss_fn=nn.CrossEntropyLoss()
    def evaluate(loader):
      model.eval();correct=total=loss_sum=0
      with torch.inference_mode():
        for x,y in loader:
          x,y=x.to(device),y.to(device);logits=model(x);loss_sum+=loss_fn(logits,y).item()*len(y);correct+=(logits.argmax(1)==y).sum().item();total+=len(y)
      return {"loss":loss_sum/max(total,1),"accuracy":correct/max(total,1),"samples":total}
    best=-1;best_state=None
    for epoch in range(1,a.epochs+1):
      model.train();total=correct=loss_sum=0
      for x,y in loaders[0]:
        x,y=x.to(device),y.to(device);opt.zero_grad(set_to_none=True);logits=model(x);loss=loss_fn(logits,y);loss.backward();opt.step()
        loss_sum+=loss.item()*len(y);correct+=(logits.argmax(1)==y).sum().item();total+=len(y)
      val=evaluate(loaders[1]);print(f"epoch={epoch}/{a.epochs} train_loss={loss_sum/max(total,1):.4f} train_acc={correct/max(total,1):.4f} val_acc={val['accuracy']:.4f}")
      if val["accuracy"]>best:best=val["accuracy"];best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
    model.load_state_dict(best_state);test=evaluate(loaders[2]);a.output_dir.mkdir(parents=True,exist_ok=True)
    torch.save({"state_dict":model.cpu().state_dict(),"architecture":"resnet18","class_names":base.classes},a.output_dir/"plant_disease_resnet18.pt")
    (a.output_dir/"class_names.json").write_text(json.dumps(base.classes,indent=2),encoding="utf-8")
    (a.output_dir/"training_metrics.json").write_text(json.dumps({"device":str(device),"seed":a.seed,"classes":len(base.classes),"class_names":base.classes,"best_validation_accuracy":best,"test":test},indent=2),encoding="utf-8")
    print(f"Saved checkpoint to {a.output_dir}; held-out metrics: {test}")
    print("Image-level random splits can overstate performance. Check duplicates and validate with external field images.")
if __name__=="__main__":main()
