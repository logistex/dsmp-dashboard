# coding: utf-8
# 대시보드 조립기: 대시보드 현황/*.json(세션 자가 보고)을 모아 data.json을 만듦.
# 쉬는 세션은 STATIC 기본값으로 채우고, 파일이 있으면 (machine,name)로 그 값을 덮음.
import json, glob, os, subprocess, sys

PROJ = "/Users/logistex/Library/CloudStorage/SynologyDrive-Me/연도/yr26/DS26/vibe coding for DSMP"
STATUS_DIR = os.path.join(PROJ, "대시보드 현황")
HERE = os.path.dirname(os.path.abspath(__file__))

def kst_now():
    return subprocess.check_output(["bash","-lc","TZ=Asia/Seoul date '+%Y-%m-%d %H:%M'"]).decode().strip()+" KST"

DEADLINES = [
    {"label":"7장 완성","when":"11/8(일) 밤"},
    {"label":"7장 수업","when":"11/12(목) A · 11/13(금) B"},
    {"label":"8장 준비","when":"~11/24(화)"},
    {"label":"8장 수업","when":"11/26 주간"},
    {"label":"기말 공고","when":"12/1(화)"},
    {"label":"기말 마감","when":"12/14(월)"},
]
CHAPTERS = [
    {"name":"7장 강의노트(영상 포함)","status":"work","pct":94,
     "lines":["7.3·7.4절 공개 완료","7.5~7.6절 영상(V31~V38) 편집·검사 전편 통과(검토 대기)","남은 것: 녹화 세션의 7.5절 이후 노션 반영"]},
    {"name":"8장 강의노트(영상 포함)","status":"wait","pct":35,
     "lines":["개념 영상 4편 관문 통과 · VM 없는 준비 완료","리허설·녹화 11/10~11(프로) 뒤 노션 반영"]},
    {"name":"기말 과제","status":"work","pct":45,
     "lines":["채점 설계 진행(앱 25 + 보고서 15)","공고 12/1 · 11/9 뒤 실측으로 변별력 확정"]},
]
# 쉬는/끝난 세션 기본값(자가 보고 파일이 없으면 이 값을 씀)
STATIC = [
    {"machine":"프로","name":"DSMP 총괄 1105-02","role":"전체 지휘·조율","state":"work","ctx":"50%","issues":["세션 조율·기한 관리","현황판 유지·외부 회신 추적"]},
    {"machine":"프로","name":"7장 편집 1106-02","role":"7.5절 비밀값 검사","state":"work","ctx":"29%","issues":["V31·V33·V36·V37 검사 통과","V35 통과(logistex는 공개 핸들로 안 가림)","V34·V38 검사 대기"]},
    {"machine":"프로","name":"7장 녹화(VM) 1105-03","role":"녹화·노트 반영","state":"wait","ctx":"?","issues":["녹화 전부 완료","7.5절 노트 반영은 편집 관문 통과 뒤"]},
    {"machine":"프로","name":"7장 편집 1106-01","role":"7장 편집(V19~V30)","state":"done","ctx":"84%","issues":["편집 완료, 후속 1106-02에 인계"]},
    {"machine":"프로","name":"8장 노트 1105-01","role":"8장(에어로 이관)","state":"wait","ctx":"—","issues":["8장 작업은 에어가 맡음"]},
    {"machine":"에어","name":"7장 편집 1106-02","role":"7.5절 편집(V31~V38)","state":"work","ctx":"?","issues":["V34·V35·V38 합성·검토","완성분 프로에 검사 넘김"]},
    {"machine":"에어","name":"8장 노트 1105-01","role":"목소리 생성·8장","state":"wait","ctx":"?","issues":["7장 목소리 완료","8장은 리허설·녹화 뒤 대기"]},
    {"machine":"에어","name":"기말 과제 1105-05","role":"기말 채점 설계","state":"work","ctx":"?","issues":["채점 설계 문서 정리","11/9 뒤 실측 대기"]},
    {"machine":"에어","name":"기말 과제 1105-02","role":"기말 설계·에어 조율","state":"work","ctx":"?","issues":["에어 현황 규약 운영","설계·중계"]},
]

def load_files():
    out={}
    for f in glob.glob(os.path.join(STATUS_DIR,"*.json")):
        try:
            d=json.load(open(f,encoding="utf-8"))
            if d.get("machine") and d.get("name"):
                out[(d["machine"],d["name"])]=d
        except Exception as e:
            print("skip",f,e,file=sys.stderr)
    return out

def main():
    files=load_files()
    sessions=[]
    seen=set()
    for s in STATIC:
        key=(s["machine"],s["name"])
        seen.add(key)
        f=files.get(key)
        if f:
            s={"machine":f.get("machine",s["machine"]),"name":f.get("name",s["name"]),
               "role":f.get("role",s["role"]),"state":f.get("state",s["state"]),
               "ctx":f.get("ctx",s["ctx"]),"issues":f.get("issues",s["issues"])}
        sessions.append(s)
    # STATIC에 없는 파일(새 세션)도 더함
    for key,f in files.items():
        if key not in seen:
            sessions.append({"machine":f["machine"],"name":f["name"],"role":f.get("role",""),
                             "state":f.get("state","work"),"ctx":f.get("ctx","?"),"issues":f.get("issues",[])})
    # 상태 정렬: work -> wait -> done, 그 안에서 프로 먼저
    order={"work":0,"wait":1,"done":2}
    sessions.sort(key=lambda s:(order.get(s["state"],9), 0 if s["machine"]=="프로" else 1))
    data={"updated":kst_now(),"deadlines":DEADLINES,"chapters":CHAPTERS,"sessions":sessions}
    json.dump(data,open(os.path.join(HERE,"data.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print("built data.json:",data["updated"],"sessions",len(sessions),
          "from_files",len(files))

if __name__=="__main__":
    main()
