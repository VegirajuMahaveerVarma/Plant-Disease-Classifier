"""Evaluate a saved checkpoint on an independent ImageFolder directory."""
import argparse,json
from pathlib import Path
import torch
from sklearn.metrics import classification_report,confusion_matrix
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets,models,transforms

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--data-dir",type=Path,required=True);p.add_argument("--checkpoint",type=Path,required=True)
 p.add_argument("--output",type=Path,default=Path("reports/evaluation.json"));p.add_argument("--batch-size",type=int,default=32)
 a=p.parse_args();dev=torch.device("cuda" if torch.cuda.is_available() else "cpu")
 ds=datasets.ImageFolder(a.data_dir,transform=transforms.Compose([transforms.Resize((224,224)),transforms.ToTensor(),transforms.Normalize([.485,.456,.406],[.229,.224,.225])]))
 ck=torch.load(a.checkpoint,map_location=dev,weights_only=True);classes=ck.get("class_names",ds.classes)
 if classes!=ds.classes:raise SystemExit("Dataset class order does not match checkpoint class mapping")
 model=models.resnet18(weights=None);model.fc=nn.Linear(model.fc.in_features,len(classes));model.load_state_dict(ck["state_dict"]);model.to(dev).eval()
 ys=[];ps=[]
 with torch.inference_mode():
  for x,y in DataLoader(ds,batch_size=a.batch_size,shuffle=False,num_workers=0):
   ps.extend(model(x.to(dev)).argmax(1).cpu().tolist());ys.extend(y.tolist())
 report=classification_report(ys,ps,target_names=classes,output_dict=True,zero_division=0)
 result={"classification_report":report,"confusion_matrix":confusion_matrix(ys,ps).tolist(),"samples":len(ys),"classes":classes}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2),encoding="utf-8")
 print(json.dumps({"samples":len(ys),"macro_f1":report["macro avg"]["f1-score"],"accuracy":report["accuracy"],"output":str(a.output)},indent=2))
if __name__=="__main__":main()
