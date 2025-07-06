import requests
import re
import json
from colorama import init, Fore, Style
from urllib.parse import urlparse
from typing import List, Dict

# 初始化颜色设置
init(autoreset=True)

def display_menu() -> None:
    """显示主菜单"""
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + "==================== e春秋自动刷课程序 ====================")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "1. 开始刷课")
    print(Fore.YELLOW + "2. 退出程序")

def get_base_url() -> str:
    """获取基础URL"""
    url_input = input(Fore.MAGENTA + "请输入课程列表链接（如：http://218.199.190.122:806）：\n" + Style.RESET_ALL)
    parsed_url = urlparse(url_input)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def fetch_package_ids(session: requests.Session, base_url: str) -> List[str]:
    """获取课程包ID列表"""
    package_ids = []
    package_regex = re.compile(r'name="" packageid="(.*?)"')
    
    for page in range(2, 11):
        url = f"{base_url}/index.php/Book/lists?per_page={page}"
        try:
            response = session.get(url)
            response.raise_for_status()
            package_ids.extend(package_regex.findall(response.text))
        except requests.RequestException as e:
            print(Fore.RED + f"获取第 {page} 页课程失败: {str(e)}")
    
    return package_ids

def process_course(session: requests.Session, base_url: str, package_id: str) -> None:
    """处理单个课程"""
    # 创建学习任务
    create_url = f"{base_url}/index.php/Book/createstudy"
    try:
        response = session.post(create_url, data={"packageid": package_id})
        response.raise_for_status()
        task_id = json.loads(response.text)['data']['taskid']
        print(Fore.GREEN + f"开始处理任务: {task_id}")
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print(Fore.RED + f"创建学习任务失败: {str(e)}")
        return
    
    # 获取章节ID
    section_regex = re.compile(r'sectioninsid=(.*?)"')
    detail_url = f"{base_url}/index.php/Study/studydetail?taskid={task_id}"
    try:
        response = session.get(detail_url)
        response.raise_for_status()
        section_ids = section_regex.findall(response.text)
    except requests.RequestException as e:
        print(Fore.RED + f"获取章节信息失败: {str(e)}")
        return
    
    # 处理章节学习
    score_url = f"{base_url}/index.php/Study/sectionScore/"
    for section_id in section_ids:
        for score_type in ["2", "3"]:  # 合并type=2和type=3的请求
            try:
                response = session.post(
                    score_url, 
                    data={
                        "sectioninsid": section_id,
                        "taskid": task_id,
                        "type": score_type
                    }
                )
                response.raise_for_status()
                print(Fore.YELLOW + f"章节 {section_id} ({score_type}): {response.text}")
            except requests.RequestException as e:
                print(Fore.RED + f"提交章节分数失败: {str(e)}")
    
    # 结束学习
    end_url = f"{base_url}/index.php/Study/endstudy"
    try:
        session.post(end_url, data={"taskid": task_id})
        print(Fore.GREEN + f"完成任务: {task_id}")
    except requests.RequestException as e:
        print(Fore.RED + f"结束学习失败: {str(e)}")

def run_shuake(cookie: str, base_url: str) -> None:
    """执行刷课主流程"""
    with requests.Session() as session:
        session.headers.update({"Cookie": cookie})
        
        print(Fore.BLUE + "正在获取课程列表...")
        package_ids = fetch_package_ids(session, base_url)
        
        if not package_ids:
            print(Fore.RED + "未找到任何课程!")
            return
        
        print(Fore.BLUE + f"找到 {len(package_ids)} 门课程，开始处理...")
        
        for idx, package_id in enumerate(package_ids, 1):
            print(Fore.CYAN + f"\n处理课程 {idx}/{len(package_ids)} (ID: {package_id})")
            process_course(session, base_url, package_id)

def main() -> None:
    """主程序入口"""
    while True:
        display_menu()
        choice = input(Fore.MAGENTA + "请选择操作 (1-2): " + Style.RESET_ALL).strip()
        
        if choice == "1":
            cookie = input(Fore.MAGENTA + "请输入Cookie：\n" + Style.RESET_ALL)
            base_url = get_base_url()
            run_shuake(cookie, base_url)
            input(Fore.BLUE + "按回车键返回主菜单..." + Style.RESET_ALL)
        elif choice == "2":
            print(Fore.RED + "程序已退出。")
            break
        else:
            print(Fore.RED + "无效选项，请重新输入。")

if __name__ == "__main__":
    main()
