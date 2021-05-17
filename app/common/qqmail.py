# 邮件发送
# 可以考虑一下邮件轰炸,但不要用自己的邮箱了哈
# 发送的邮件是可以看到ip地址的, 小心使用


## 通过sendmail发送邮件
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEBase  # 附件
from email import encoders
from email.mime.application import MIMEApplication

# 使用方法：
# receivers: 收件人
# message： MIME类型的邮件
def sendEmailByQQ(receivers, message):
    '用我的qq邮箱进行邮件发送'
    sender = '1105711978@qq.com' # os.getenv('MAIL_QQ') # qq邮箱作为代理邮箱
    password = 'shomufxjhbtpjbeg' # os.getenv('MAIL_QQ_AUTH_CODE') # qq邮箱授权码
   
    # 发送邮件
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.qq.com') # 连接服务器 ssl加密方式
        smtpObj.ehlo()
        print('successfully conntect to qq smtp')
        # smtpObj.starttls() # 建立安全链接, 加密防止窃听
        smtpObj.login(sender, password)  # 登陆服务器
        print('sending email, please wait...')
        # smtpObj.sendmail(sender, receivers, message.as_string()) # 发送邮件
        smtpObj.sendmail(sender, receivers, message.as_bytes()) # 发送邮件
        print('send successfully')
        
    except Exception as e:
        print('Error: failed to send email with', e)
        return False
    else:
        return True
    finally:
        smtpObj.quit()  # 关闭连接

# title标题, content邮件正文, footer脚注
def sendAlertToMe(title='Alert', content='python通知邮件', contentType='plain', sender="pythonAlert"):
    'alert接收一个字符串，作为邮件标题'
    receivers = '1105711978@qq.com'
    message = MIMEMultipart()  # 多内容邮件对象
    try:
        message.attach(MIMEText(content, contentType, 'utf-8'))  # 邮件正文, plain代表纯文本
        message['From'] = Header(sender+' <pythonEmail@knavem.xyz>', 'utf-8')  # 发送者
        message['To'] = Header('ZYX <1105711978@qq.com>', 'utf-8')  # 接收者 固定
        message['Subject'] = Header('['+sender+']'+title, 'utf-8')  # 邮件标题
    except Exception as e: print("Error occurs while creating MIMEText",e)
    else: sendEmailByQQ(receivers, message)

if __name__ == '__main__':
    # 收件人
    receivers = '1105711978@qq.com'

    # 构造邮件
    message = MIMEMultipart()  # 多内容邮件对象
    
    subject = 'english pronunciation'
    message.attach(MIMEText('Python 邮件测试', 'plain', 'utf-8'))  # 邮件正文, plain代表纯文本
    
    message['From'] = Header('python007<pythonEmail>', 'ascii')  # 发送者
    message['To'] = Header('myself<1105711978@qq.com>', 'utf-8')  # 接收者
    message['Subject'] = Header(subject, 'utf-8')  # 邮件标题

    #添加附件
    # fileName = 'chinese culture symbol.pptx'
    # filePath = r'C:\Users\11057\Desktop\presentation\%s' % fileName

    # attachment = MIMEApplication(open(filePath, 'rb').read())
    # attachment.add_header('Content-Disposition', 'attachment', filename=fileName)
    # message.attach(attachment)

    # sendEmailByQQ(receivers, message)
    sendAlertToMe('test')


