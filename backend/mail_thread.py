import threading
import smtplib
from email.mime.text import MIMEText
from email.header import Header


sender = 'deepthu@163.com'
username = 'deepthu'
password = 'deepthu0036'
smtpServer = 'smtp.163.com'


class MailThread(threading.Thread):

    def __init__(self, task_id, dst_addr, state):
        threading.Thread.__init__(self)
        self.task_id = task_id
        self.dst_addr = dst_addr
        self.state = state

    def run(self):
        if self.state == 'CREATED':
            title = 'deepTHU——任务创建完成'
            body = """
            <p>您的任务创建完成，任务id为:<b>%s</b>。</p>
            <p>请妥善保管您的任务id，您可以随时使用id在主页查询任务状态。</p>
            <p>deepTHU</p>
            """ % self.task_id
        elif self.state == 'FINISHED':
            title = 'deepTHU——任务完成'
            body = """
            <p>您的任务:<b>%s</b>已完成。</p>
            <p>请妥善保管您的任务id，您可以随时使用id在主页下载您的结果文件。</p>
            <p>请注意您的任务从创建起最多在我们的服务器上保存30天，过期将会自动删除。</p>
            <p>deepTHU</p>
            """ % self.task_id
        message = MIMEText(body, 'html', 'utf-8')
        message['From'] = sender
        message['To'] = self.dst_addr
        message['Subject'] = Header(title, 'utf-8')

        try:
            smtp = smtplib.SMTP()
            smtp.connect(smtpServer)
            smtp.login(username, password)
            smtp.sendmail(sender, self.dst_addr, message.as_string())
            smtp.quit()
        except:
            pass
