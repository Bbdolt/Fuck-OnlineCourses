# enc = md5()"[clazzId][userid][jobid][objectId][playingTime * 1000][d_yHJ!$pdA~5][duration * 000][0_'duration']")
# 参与签名参数: clazzId, userid, jobid, objectId, playingTime, duration
# https://mooc1.chaoxing.com/mooc-ans/knowledge/cards?clazzid=70294178&courseid=207288462&knowledgeid=220381766 获取参数
# 通过 objectId 参数获取 https://mooc1.chaoxing.com/mooc-ans/multimedia/log/a/291645895/e964a5d65290e7e51096a2b8aa302e85?clazzId=70294178&playingTime=503&duration=542&objectId=a07a3364a4eb67878e40dfac445644fb&otherInfo=nodeId_220381766-cpi_291645895-rt_d-ds_1-ff_d-be_0_0-vt_1-v_6-enc_775b9e3907db44729b62ee1a323a1dd7&jobid=1583983028605973&userid=242776885&isdrag=0&view=pc&enc=be1df007fecce5dc811ee6ba7b9ad612 中的 e964a5d65290e7e51096a2b8aa302e85
# 通过链接 https://mooc1.chaoxing.com/ananas/status/a07a3364a4eb67878e40dfac445644fb
# 通过这个链接表示完成 https://mooc1.chaoxing.com/mooc-ans/multimedia/log/a/291645895/e964a5d65290e7e51096a2b8aa302e85?clazzId=70294178&playingTime=503&duration=542&objectId=a07a3364a4eb67878e40dfac445644fb&otherInfo=nodeId_220381766-cpi_291645895-rt_d-ds_1-ff_d-be_0_0-vt_1-v_6-enc_775b9e3907db44729b62ee1a323a1dd7&jobid=1583983028605973&userid=242776885&isdrag=0&view=pc&enc=be1df007fecce5dc811ee6ba7b9ad612

# 通过 https://mooc2-ans.chaoxing.com/mooc2-ans/visit/courselistdata 获取 clazzid, courseid 参数
# 通过 https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/studentcourse?courseid=230809436&clazzid=105255308 获取 knowledgeid
import time
import requests
from lxml import etree
import warnings
from tabulate import tabulate
import re
import hashlib
import json
import os
import sys
from colorama import init, Fore, Back, Style

# 初始化colorama，支持Windows彩色输出
init(autoreset=True)

# 忽略SSL警告
warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()

PROXIES = {
    'http': 'http://127.0.0.1:8888',
    'https': 'http://127.0.0.1:8888'
}

def clear_screen():
    """清屏函数"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_success(msg):
    """打印成功信息（绿色）"""
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_error(msg):
    """打印错误信息（红色）"""
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_warning(msg):
    """打印警告信息（黄色）"""
    print(f"{Fore.YELLOW}⚠ {msg}{Style.RESET_ALL}")

def print_info(msg):
    """打印信息（蓝色）"""
    print(f"{Fore.BLUE}ℹ {msg}{Style.RESET_ALL}")

def print_progress(msg, end="\n"):
    """打印进度信息（青色）"""
    if end == "\r":
        # 清除当前行并重新打印
        sys.stdout.write("\r" + " " * 80)  # 清除当前行
        sys.stdout.write(f"\r{Fore.CYAN}→ {msg}{Style.RESET_ALL}")
        sys.stdout.flush()
    else:
        print(f"{Fore.CYAN}→ {msg}{Style.RESET_ALL}", end=end)

def print_progress_update(msg):
    """更新进度信息（不换行）"""
    print_progress(msg, end="\r")

def print_progress_final(msg):
    """最终进度信息（换行）"""
    print_progress(msg, end="\n")

class ChaoxingBot:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }
        self.userid = None
        self.cookie = None
        self.is_logged_in = False
        self.user_name = None
        self.school_name = None

    def set_cookie(self, cookie):
        """设置Cookie并提取userid"""
        self.cookie = cookie
        self.headers["Cookie"] = cookie
        obj_userid = re.compile(r'_uid=(.*?);')
        userid_match = re.findall(obj_userid, cookie)
        if userid_match:
            self.userid = userid_match[0]
            self.is_logged_in = True
            # 获取用户信息
            self.get_user_info()
            print_success("登录成功！")
            return True
        else:
            print_error("Cookie格式错误，未找到userid")
            return False

    def get_user_info(self):
        """获取用户信息"""
        try:
            url = "https://i.chaoxing.com/base"
            with requests.get(url, headers=self.headers) as r:
                html = etree.HTML(r.text)
                elements = html.xpath('//*[contains(@class, "user-name")]')
                if elements:
                    self.user_name = elements[0].text.strip()
                else:
                    self.user_name = "未知用户"
                
                elements1 = html.xpath('//*[contains(@id, "siteName")]')
                if elements1:
                    self.school_name = elements1[0].text.strip()
                else:
                    self.school_name = "未知单位"
        except Exception as e:
            print_error(f"获取用户信息失败：{e}")
            self.user_name = "未知用户"
            self.school_name = "未知单位"

    def get_enc(self, clazzId, userid, jobid, objectid, playingTime, duration):
        """生成加密签名"""
        strings = f"[{clazzId}][{userid}][{jobid}][{objectid}][{playingTime * 1000}][d_yHJ!$pdA~5][{duration * 1000}][0_{duration}]"
        md5_hash = hashlib.md5(strings.encode('utf-8')).hexdigest()
        return md5_hash

    def get_all_params(self, mArg_dict, clazzId, curPersonId, knowledgeid, couseid):
        """获取所有参数"""
        attachments = mArg_dict.get('attachments', [])
        infos = []
        for attachment in attachments:
            otherInfo = attachment.get('otherInfo', '').split('&')[0]
            type_name = attachment.get('type', '')
            if type_name == "workid":
                print(attachment)
            jobid = attachment.get('jobid', '')
            if jobid == "":
                jobid = attachment.get('property', {}).get('_jobid', '')
            objectid = attachment.get('objectId', '')
            duration = attachment.get('attDuration', 0)
            jtoken = attachment.get('jtoken', '')
            playingTime = int(attachment.get('playTime', duration * 1000 - 100000) / 1000)
            isdrag = 0
            view = "pc"
            enc = self.get_enc(clazzId, self.userid, jobid, objectid, playingTime, duration)
            infos.append([clazzId, playingTime, duration, objectid, otherInfo, jobid, self.userid, isdrag, view, enc, curPersonId, type_name, jtoken, knowledgeid, couseid])
        return infos

    def get_course_list(self):
        """获取课程列表"""
        if not self.is_logged_in:
            print_error("请先登录！")
            return []

        print_progress_final("正在获取课程列表...")
        url = "https://mooc2-ans.chaoxing.com/mooc2-ans/visit/courselistdata"
        params = {
            "courseType": "1",
            "courseFolderId": "0",
            "query": "",
            "pageHeader": "-1",
            "single": "0",
            "superstarClass": "0"
        }
        
        course_info = []
        response = requests.post(url, headers=self.headers, data=params)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            course_divs = html.xpath('//div[contains(@class, "course") and contains(@class, "clearfix")]')
            clazzPersonStr = []
            for course in course_divs:
                try:
                    clazzId = course.xpath('.//input[@class="clazzId"]/@value')[0]
                    courseId = course.xpath('.//input[@class="courseId"]/@value')[0]
                    curPersonId = course.xpath('.//input[@class="curPersonId"]/@value')[0]
                    course_name = course.xpath('.//span[@class="course-name overHidden2"]/text()')[0].strip()
                    course_info.append([clazzId, courseId, curPersonId, course_name])
                    clazzPersonStr.append(f"{clazzId}_{curPersonId}")
                except Exception as e:
                    print_error(f"解析课程信息时出错：{e}")

            # 新增：获取课程进度信息
            progress_dict = {}
            url6 = f"https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/stu-job-info"
            params6 = "clazzPersonStr=" + ",".join(clazzPersonStr)
            try:
                response6 = requests.get(url6, headers=self.headers, params=params6).json()
                jobArray = response6.get('jobArray', [])
                for job in jobArray:
                    clazzId = str(job.get("clazzId"))
                    jobRate = job.get("jobRate")
                    if jobRate is not None:
                        progress_dict[clazzId] = f"{jobRate:.1f}%"
                    else:
                        progress_dict[clazzId] = "--"
            except Exception as e:
                print_error(f"获取课程进度信息失败：{e}")

            # 新增：为每门课程添加进度字段
            headers_show = ["序号", "班级ID", "课程ID", "当前用户ID", "课程名称", "进度"]
            table_data = []
            for i, row in enumerate(course_info):
                clazzId = str(row[0])
                progress = progress_dict.get(clazzId, "--")
                if progress != "--":
                    table_data.append([i + 1] + row + [progress])

            print(f"\n{Fore.MAGENTA}📚 课程列表{Style.RESET_ALL}")
            print(tabulate(table_data, headers=headers_show, tablefmt="fancy_grid"))
            
            return course_info
        else:
            print_error(f"获取课程列表失败，状态码：{response.status_code}")
            return []

    def get_dtoken(self, objectid):
        """获取dtoken"""
        if objectid == "":
            return False, "objectid 值为空"
        url = f"https://mooc1.chaoxing.com/ananas/status/{objectid}"
        headers_copy = self.headers.copy()
        headers_copy['Referer'] = "https://mooc1.chaoxing.com"
        response = requests.get(url, headers=headers_copy)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            dtoken = json_data.get('dtoken', '')
            return True, dtoken
        else:
            return False, f"获取 dtoken 失败，状态码：{response.status_code}"

    def get_isPassed(self, response_text):
        try:
            json_data = json.loads(response_text)
            isPassed = json_data.get('isPassed', False)
            return isPassed
        except json.JSONDecodeError as e:
            return False

    def start_auto_study(self):
        """开始自动刷课"""
        if not self.is_logged_in:
            print_error("请先登录！")
            return

        # 获取课程列表
        course_info = self.get_course_list()
        if not course_info:
            print_error("没有找到课程信息")
            return

        # 选择课程
        try:
            index = int(input(f"{Fore.YELLOW}请输入要刷的课程序号：{Style.RESET_ALL}")) - 1
            if index < 0 or index >= len(course_info):
                print_error("无效的课程序号！")
                return
        except ValueError:
            print_error("请输入有效的数字！")
            return

        selected_course = course_info[index]
        print_success(f"已选择课程：{selected_course[3]}")
        
        # 获取knowledgeid列表
        print_progress_final("正在获取章节信息...")
        obj1 = re.compile(r'onclick="toOld\((.*?)\)"')
        course_info1 = []
        url1 = "https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/studentcourse"
        params1 = {
            "courseid": selected_course[1],
            "clazzid": selected_course[0]
        }
        
        with requests.session() as session:
            session.headers.update(self.headers)
            response1 = session.get(url1, headers=self.headers, params=params1)
            knowledgeid_list = obj1.findall(response1.text)
            for ii in knowledgeid_list:
                knowledgeid = ii.split(',')[1].replace('\'', '').strip()
                course_info1.append([
                    selected_course[0], selected_course[1], knowledgeid, selected_course[2], selected_course[3]
                ])

        print_info(f"共有 {len(course_info1)} 个章节")

        # 获取所有视频参数
        print_progress_final("正在获取视频信息...")
        course_info2 = []
        url2 = "https://mooc1.chaoxing.com/mooc-ans/knowledge/cards"
        params2 = {
            "clazzid": "",
            "courseid": "",
            "knowledgeid": "",
        }
        
        with requests.session() as session:
            session.headers.update(self.headers)
            for i, course2 in enumerate(course_info1):
                print_progress_update(f"正在处理第 {i+1}/{len(course_info1)} 个章节...")
                clazzId = course2[0]
                params2['clazzid'] = clazzId
                params2['courseid'] = course2[1]
                params2['knowledgeid'] = course2[2]
                curPersonId = course2[3]
                response2 = session.get(url2, headers=self.headers, params=params2)

                if response2.status_code == 200:
                    html2 = etree.HTML(response2.text)
                    js_code = html2.xpath('/html/body/script[1]/text()')[0]
                    match = re.search(r'mArg\s*=\s*({.*?})\s*;', js_code, re.DOTALL)
                    if match:
                        mArg_str = match.group(1)
                        mArg_str = mArg_str.replace("true", "true".lower())
                        mArg_str = mArg_str.replace("false", "false".lower())
                        mArg_str = mArg_str.replace("null", "null".lower())

                        try:
                            mArg_dict = json.loads(mArg_str)
                            course_info2 += self.get_all_params(mArg_dict, clazzId, curPersonId, params2['knowledgeid'], params2['courseid'])
                        except json.JSONDecodeError as e:
                            print_error(f"JSON 解析失败：{e}")
                    else:
                        print_warning(f"第 {i+1} 章节未找到 mArg 内容: clazzId:{clazzId},couseid:{params2['courseid']},knowledgeid:{params2['knowledgeid']}")

        print_progress_final(f"共有 {len(course_info2)} 个视频")

        # 开始刷课
        print_progress_final("开始自动刷课...")
        success_count = 0
        with requests.session() as session:
            for i, course3 in enumerate(course_info2):
                print_progress_update(f"正在处理第 {i+1}/{len(course_info2)} 个任务点...")
                clazzId = course3[0]
                playingTime = course3[1]
                duration = course3[2]
                objectid = course3[3]
                otherInfo = course3[4]
                jobid = course3[5]
                userid = course3[6]
                isdrag = course3[7]
                view = course3[8]
                enc = course3[9]
                curPersonId = course3[10]
                type_name = course3[11]
                jtoken = course3[12]
                knowledgeid1 = course3[13]
                couseid1 = course3[14]
                # isdrag: 0 playing, 1 drag, 2 pause, 3 play, 4 ended
                # 0 playing：播放中
                # 1 drag：拖动（进度条）
                # 2 pause：暂停
                # 3 play：播放
                # 4 ended：已结束
                min_duration = int(duration * 0.8)

                # type_name: workid(作业), video(视频), document(文档), 无
                if type_name == 'video':
                    # 获取 dtoken
                    success, dtoken = self.get_dtoken(objectid)
                    if success:
                        # 开始刷课
                        url4 = "https://mooc1.chaoxing.com/mooc-ans/multimedia/log/a/" + str(curPersonId) + "/" + dtoken
                        params3 = {
                            "clazzId": clazzId,
                            "playingTime": playingTime,
                            "duration": duration,
                            "objectId": objectid,
                            "otherInfo": otherInfo,
                            "jobid": jobid,
                            "userid": userid,
                            "isdrag": 0,
                            "view": "pc",
                            "enc": enc,
                        }
                        response4 = session.get(url4, headers=self.headers, params=params3)
                        isPassed = self.get_isPassed(response4.text)
                        if isPassed:
                            success_count += 1
                        else:
                            can_do = False
                            range_list = [1, 0.9126, 0.9726, 0.9326, 0.9226, 0.9426, 0.9526, 0.9926, 0.8626, 0.8926]
                            for rate in range_list:
                                playingTime = int(duration * rate)
                                enc = self.get_enc(clazzId, userid, jobid, objectid, playingTime, duration)
                                params3['playingTime'] = playingTime
                                params3['enc'] = enc
                                response6 = session.get(url4, headers=self.headers, params=params3)
                                isPassed3 = self.get_isPassed(response6.text)
                                if isPassed3:
                                    success_count += 1
                                    can_do = True
                                    break
                            if not can_do:
                                print_error(f"[{knowledgeid1}]视频 {i+1} 刷课失败")
                    else:
                        print_error(dtoken)
                # 教材为文档的情况
                # 需要参数 jobid, knowledgeid, courseid, clazzid, jtoken
                elif type_name == "document":
                    url5 = "https://mooc1.chaoxing.com/ananas/job/document"
                    params5 = {
                        "jobid": jobid,
                        "knowledgeid": knowledgeid1,
                        "courseid": couseid1,
                        "clazzid": clazzId,
                        "jtoken": jtoken
                    }
                    response5 = session.get(url5, headers=self.headers, params=params5)
                    if response5.status_code == 200:
                        result5 = json.loads(response5.text)
                        if result5['status']:
                            success_count += 1
                        else:
                            print_warning(f"[{knowledgeid1}]文档 {i+1} 未完成")
                    else:
                         print_error(f"文档 {i+1} 刷课失败")
                # 教材为空的情况
                elif type_name == "workid":
                    pass
                else:
                    print(f"{knowledgeid1} 内容为空")

        # 显示最终结果
        print(f"\n{Fore.MAGENTA}🎉 刷课完成！{Style.RESET_ALL}")
        print_success(f"成功完成 {success_count}/{len(course_info2)} 个视频")

    def logout(self):
        """退出登录"""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }
        self.userid = None
        self.cookie = None
        self.is_logged_in = False
        self.user_name = None
        self.school_name = None
        print_success("已退出登录")

def show_header(bot):
    """显示程序头部信息"""
    clear_screen()
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*20} 超星学习通自动刷课程序 {'='*20}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    if bot.is_logged_in and bot.user_name and bot.school_name:
        print(f"{Fore.GREEN}👤 当前用户：{bot.user_name}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🏫 归属单位：{bot.school_name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*60}{Style.RESET_ALL}")

def main():
    bot = ChaoxingBot()
    
    while True:
        show_header(bot)
        
        if not bot.is_logged_in:
            print(f"{Fore.YELLOW}1. 输入Cookie登录{Style.RESET_ALL}")
            print(f"{Fore.RED}2. 退出程序{Style.RESET_ALL}")
            choice = input(f"{Fore.CYAN}请选择操作 (1-2): {Style.RESET_ALL}")
            
            if choice == "1":
                cookie = input(f"{Fore.YELLOW}请输入Cookie: {Style.RESET_ALL}")
                if bot.set_cookie(cookie):
                    input(f"{Fore.GREEN}按回车键继续...{Style.RESET_ALL}")
            elif choice == "2":
                print(f"{Fore.CYAN}程序退出{Style.RESET_ALL}")
                break
            else:
                print_error("无效选择，请重新输入")
                input(f"{Fore.YELLOW}按回车键继续...{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}1. 查看课程表{Style.RESET_ALL}")
            print(f"{Fore.BLUE}2. 开始刷课{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}3. 退出登录{Style.RESET_ALL}")
            print(f"{Fore.RED}4. 退出程序{Style.RESET_ALL}")
            choice = input(f"{Fore.CYAN}请选择操作 (1-4): {Style.RESET_ALL}")
            
            if choice == "1":
                bot.get_course_list()
                input(f"{Fore.GREEN}按回车键继续...{Style.RESET_ALL}")
            elif choice == "2":
                bot.start_auto_study()
                input(f"{Fore.GREEN}按回车键继续...{Style.RESET_ALL}")
            elif choice == "3":
                bot.logout()
                input(f"{Fore.GREEN}按回车键继续...{Style.RESET_ALL}")
            elif choice == "4":
                print(f"{Fore.CYAN}程序退出{Style.RESET_ALL}")
                break
            else:
                print_error("无效选择，请重新输入")
                input(f"{Fore.YELLOW}按回车键继续...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()