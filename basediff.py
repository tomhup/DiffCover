import re
import os
import shutil
import operator

from git import Repo





class RunDiff():
    def __init__(self,project_dir,old_version,repo_dir,jacoco_dir,diff_dir):
        self.project_dir = project_dir
        self.old_version = old_version  #比对的版本号
        self.repo = Repo(repo_dir)
        self.jacoco_dir = jacoco_dir
        self.diff_dir = diff_dir

    #获取文件信息
    def get_info(self,full_path,file_name):
        package = self.get_package(full_path)
        class_name = re.search('(\w+)\.java$', file_name).group(1)
        return (package, class_name)

    #获取package包名
    def get_package(self,file_name):
        """获取package名"""
        ret = ''
        with open(file_name,encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                match = re.match('package\s+(\S+);', line)
                if match:
                    ret = match.group(1)
                    break
        return ret

    #修改jacoco报告，只点亮变更代码行
    def modify_report(self,html_file_name,diff_lines,package):
        new_line_count = 0
        cover_line_count = 0

        with open(html_file_name, 'r',encoding='utf-8', errors='ignore') as fp:
            content = fp.readlines()
        for i in range(1, len(content)):
            if i + 1 in diff_lines:
                match = re.search('class="([^"]+)"', content[i])
                if match:
                    css_class = match.group(1)
                    new_line_count += 1
                    if css_class.startswith("fc") or css_class.startswith("pc"):
                        cover_line_count += 1
            else:
                match = re.search('class="([^"]+)"', content[i])
                if match:
                    content[i] = re.sub('class="([^"]+)"','class=""', content[i])
        if new_line_count != 0:

            with open(html_file_name, 'w',encoding='utf-8') as fp:
                fp.write("".join(content))

        return new_line_count, cover_line_count


    #获取版本之间代码差异
    def get_diff(self):
        diff = self.repo.git.diff(self.old_version, self.repo.head).split("\n")
        ret = {}
        file_name = ''
        diff_lines = []
        current_line = 0
        for line in diff:
            if line.startswith('diff --git'):
                if file_name != '':
                    ret[file_name] = diff_lines
                file_name = re.findall('b/(\S+)$', line)[0]
                diff_lines = []
                current_line = 0

            elif re.match('@@ -\d+,\d+ \+(\d+),\d+ @@', line):
                match = re.match('@@ -\d+,\d+ \+(\d+),\d+ @@', line)
                current_line = int(match.group(1)) - 1

            elif line.startswith("-"):
                continue
            elif line.startswith("+") and not line.startswith('+++'):
                current_line += 1
                diff_lines.append(current_line)
            else:
                current_line += 1
        ret[file_name] = diff_lines
        return ret

    #运行代码变更覆盖率
    def run_diff(self):
        ret = []
        diff_res = self.get_diff()
        print(diff_res)
        all_line_count = 0  #总变更代码行数
        all_cover_count = 0  #总覆盖变更代码行数


        shutil.rmtree(self.diff_dir)

        shutil.copytree(os.path.join(self.jacoco_dir),os.path.join(self.diff_dir))  #将全量的覆盖率文件中的依赖文件拷到变量覆盖率文件下
        for file_name in diff_res:
            if diff_res[file_name] == []:
                continue
            if not file_name.endswith('.java') or 'src/test/java/' in file_name:
                continue
            full_path = os.path.join(self.project_dir+ '/src', file_name)
            if os.path.exists(full_path):
                package, class_name = self.get_info(full_path,file_name)
                html_file_name = os.path.join(self.diff_dir,'report_html',package, "{}.java.html".format(class_name))
                print(html_file_name)
                if os.path.exists(html_file_name):
                    new_line_count, cover_line_count = self.modify_report(html_file_name,diff_res[file_name],package)
                    if new_line_count != 0:
                        cover_rate = ('%.2f%%' % (cover_line_count/new_line_count*100))
                        all_line_count += new_line_count
                        all_cover_count += cover_line_count

                        cover_res={'package':package,'class':class_name,"new": new_line_count, "cover": cover_line_count,'cover_rate':cover_rate}
                        ret.append(cover_res)
        ret = sorted(ret,key=operator.itemgetter('package'))
        if all_line_count != 0:
            all_cover_rate = ('%.2f%%' % (all_cover_count/all_line_count*100))
            cover_res = { '': "总体", "new": all_line_count, "cover": all_cover_count,'cover_rate':all_cover_rate}
            ret.append(cover_res)
        return ret

def main():
    #项目目录
    project_dir = '/Users/pingan/eclipse-workspace/basev2'
    #代码管理目录
    repo_dir = '/Users/pingan/eclipse-workspace/basev2/src'
    #jacoco原始覆盖报告目录
    jacoco_dir = project_dir +'/report/'
    #差异代码覆盖报告目录
    diff_dir   = project_dir+'/diff_report/'

    #对比版本
    old_version ='v2'

    p = RunDiff(project_dir, old_version, repo_dir,jacoco_dir,diff_dir)
    p.get_diff()
    z=p.run_diff()
    for i in z: print (i)

if __name__ =="__main__":
    main()