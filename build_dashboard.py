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
    {"name":"7장 강의노트(영상 포함)","status":"done","pct":100,
     "lines":["7.0~7.9절 전부 공개·독립 검토 통과(기한 11/8보다 이틀 앞섬)","영상 V15~V38 전편 관문 통과·공개","학생 조건 되돌리기 완료(11/7 08:38)","남은 것: 수업 전 공개 화면 재확인(수업 당일 일)"]},
    {"name":"8장 강의노트(영상 포함)","status":"wait","pct":35,
     "lines":["개념 영상 4편 관문 통과 · VM 없는 준비 완료","리허설·녹화 11/10~11(프로) 뒤 노션 반영"]},
    {"name":"기말 과제","status":"work","pct":45,
     "lines":["채점 설계 진행(앱 25 + 보고서 15)","공고 12/1 · 11/9 뒤 실측으로 변별력 확정"]},
]
# 신 교수 할 일(교수 손이 꼭 필요한 것만. id는 고정 — 체크 상태가 유지되게 함)
TODOS = [
    {"id":"t1","label":"8장 VM 로그인·승인","when":"11/10~11 녹화 전",
     "note":"윈도 VM 크롬: 깃허브(OAuth App·저장소)·Vercel·Supabase 계정 B·노션 실습 워크스페이스. 방화벽 창 시험 1번 포함"},
    {"id":"t2","label":"기말 실측 로그인","when":"11/9 이후",
     "note":"Supabase 1번·Vercel 1번 — 앱 표 노출·미리보기 배포 확인"},
    {"id":"t3","label":"기말 과제 요약 확인·답","when":"준비되는 대로",
     "note":"성적 입력 기한·평가계획서 대응·게시 승인(요약 문서 3장 2~4번)"},
    {"id":"t4","label":"Anthropic Will 회신 확인","when":"회신이 오면",
     "note":"path1.js(앱 표 노출) 재개 여부 판단"},
    {"id":"t5","label":"7장 수업","when":"11/12(목) A · 11/13(금) B",
     "note":"공개 노트·영상으로 진행"},
    {"id":"t6","label":"massinv 공개/가림 결정","when":"편하실 때",
     "note":"교수님 다른 계정 아이디 — 영상에서 공개할지 가릴지 총괄에 알려 주시면 반영함"},
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
    # 주제 정렬: 총괄 -> 7장 -> 8장 -> 기말, 그 안에서 프로 먼저, 그 안에서 work->wait->done
    def topic_rank(s):
        n=s["name"]
        if "총괄" in n: return 0
        if "7장" in n: return 1
        if "8장" in n: return 2
        if "기말" in n: return 3
        return 4
    order={"work":0,"wait":1,"done":2}
    sessions.sort(key=lambda s:(topic_rank(s), 0 if s["machine"]=="프로" else 1, order.get(s["state"],9)))
    data={"updated":kst_now(),"deadlines":DEADLINES,"chapters":CHAPTERS,"todos":TODOS,"sessions":sessions}
    json.dump(data,open(os.path.join(HERE,"data.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print("built data.json:",data["updated"],"sessions",len(sessions),
          "from_files",len(files))

if __name__=="__main__":
    main()
