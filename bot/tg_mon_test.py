# import  section
# =================================================================================================================
import logging, re, paramiko, os
import psycopg2

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import Update, ForceReply
from psycopg2 import Error
from pathlib import Path

# =================================================================================================================
# end of import section

EMAILS = []
PHONES = []
# Enable logging
# =================================================================================================================
logging.basicConfig(filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# =================================================================================================================
# end of logging

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(
            '''Hello!
            
            Here's what I can do:
            1.  /find_email - search emails in text
            2.  /find_phone - search phones in text
            3.  /verify_password - verify password streght
            4.  /get_release - show Linux version on monitored host
            5.  /get_uptime - show uptime in monitored host
            6.  /get_df - show available space in disks on monitored host
            7.  /get_free - show memory stats on monitoref host
            8.  /get_w - show currently working  users
            9.  /get_auths - show last 10 logined users
            10. /get_critical - show last 5 critical errors
            11. /get_ps - show proccess tree
            12. /get_ss - show open sockets
            13. /get_apt_list - show information about all installed packages or inforamtion about specified package
            14. /get_services - show information about running services
            15. /get_repl_logs - show postgresql cluster replication logs
            16. /get_emails - select emails from database 
            17. /get_phone_numbers - select phones from database
            18. /help - get help about features
            ''')


def helpCommand(update: Update, context):
    '''
    Function sends greeting information to telegram user 

    return - Nothing
    '''
    update.message.reply_text(
            '''Awailable commands: 
            1.  /find_email - search emails in text
            2.  /find_phone - search phones in text
            3.  /verify_password - verify password streght
            4.  /get_release - show Linux version on monitored host
            5.  /get_uptime - show uptime in monitored host
            6.  /get_df - show available space in disks on monitored host
            7.  /get_free - show memory stats on monitoref host
            8.  /get_w - show currently working  users
            9.  /get_auths - show last 10 logined users
            10. /get_critical - show last 5 critical errors
            11. /get_ps - show proccess tree
            12. /get_ss - show open sockets
            13. /get_apt_list - show information about all installed packages or inforamtion about specified package
            14. /get_services - show information about running services 
            15. /get_repl_logs - show postgresql cluster replication logs
            16. /get_emails - select emails from database 
            17. /get_phone_numbers - select phones from database
            18. /help - get help about features
            ''')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Input text with phone numbers: ')
    return 'find_phone'


def find_phone(update: Update, context):
    logging.info('User called find_phone function')
    user_input = update.message.text
    result = ''
    phone_regex = re.compile(r'(8|\+7)(\s|\(|-)?(\d{3})(\s|\)|-)?(\d{3})(\s|-)?(\d{2})(\s|-)?(\d{2})')
    phone_list = phone_regex.findall(user_input)
    global PHONES
    PHONES = phone_list

    if not phone_list:
        update.message.reply_text('No phones in text')
        logging.info('find_phone function not found any phone.')
        return ConversationHandler.END

    for phone in phone_list:
        for c in phone:
            result+=c
        result += '\n'
    result = result[:-1]
    update.message.reply_text(result)
    update.message.reply_text('Type "Y" if you will add finded phones to database.')
    return 'add_phones'

def add_phones(update: Update, context):
    user_input = update.message.text
    global PHONES
    print(PHONES)
    logging.info('find_phone function found phone numbers. Offer to store it in database')
    if user_input == "Y":
        conn = db_conn()
        print(conn)
        if isinstance(conn, psycopg2.OperationalError):
            update.message.reply_text('Some Error was occured while conecting to DB')
            return ConversationHandler.END
        cursor = conn.cursor()
        print(cursor)
        for e in PHONES:
            print(''.join(e))
            val = ''.join(e)
            cursor.execute('INSERT INTO phones (phone) values(%s)',(val,))
            conn.commit()
        logging.info('Phones was be insert successfully')
        cursor.close()
        conn.close()
        logging.info('Connection with DB was closed')
        PHONES = []
        update.message.reply_text('Phones was saved successfully!')
        return ConversationHandler.END
    return ConversationHandler.END


def findEmailCommand(update: Update, context):
    update.message.reply_text('Input text with emails: ')
    return 'find_email'

def find_email(update: Update, context):
    logging.info('User called find_email function') 
    user_input = update.message.text
    result = ''
    email_regex = re.compile(r'((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])')
    email_list = email_regex.findall(user_input)
    global EMAILS
    EMAILS = email_list
    if not email_list:
        update.message.reply_text('No emails in text')
        logging.info('find_email function not found any email.') 
        return ConversationHandler.END

    for email in email_list:
        result+=email[0]
        result+=email[1]
        result+=email[2]
        result+='\n'
    result=result[:-1]
    update.message.reply_text(result)
    update.message.reply_text('Type "Y" if you will add finded emails to database.')
    return 'add_emails'
    
def add_emails(update: Update, context):
    user_input = update.message.text
    global EMAILS
    logging.info('find_email function found emails. Offer to store it in database') 
    if user_input == "Y":
        conn = db_conn()
        print(conn)
        if isinstance(conn, psycopg2.OperationalError):
            update.message.reply_text('Some Error was occured while conecting to DB')
            return ConversationHandler.END
        cursor = conn.cursor()
        print(cursor)
        for e in EMAILS:
            print(''.join(e))
            val = ''.join(e)
            cursor.execute('INSERT INTO emails (email) values(%s)',(val,))
            conn.commit()
        logging.info('Emails was be insert successfully')
        cursor.close()
        conn.close()
        logging.info('Connection with DB was closed')
        EMAILS = []
        update.message.reply_text('Emails was saved successfully')
        return ConversationHandler.END
    return ConversationHandler.END


def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Input password for checking it strength')
    return 'verify_password'

def verify_password(update: Update, context):
    user_input = update.message.text
    logging.info('User called verify_password function')
    password_regex = re.compile(r'^(?=.*([A-Z]){1,})(?=.*[!@#$%^&*()]{1,})(?=.*[0-9]{1,})(?=.*[a-z]{1,}).{8,100}$')
    result = password_regex.search(user_input)

    if isinstance(result, re.Match):
        update.message.reply_text('Password strong')
        return ConversationHandler.END
    update.message.reply_text('Password weak')
    return ConversationHandler.END

def GetAptCommand(update: Update, context):
    logging.info('User called get_apt_list function')
    update.message.reply_text('Type name of packet or type "all" to get info about all installed packages')   
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user_input = update.message.text
    
    if user_input == 'all':
        client = linux_conn()
        stdin, stdout, stderr = client.exec_command("dpkg -l | cut -d' ' -f3 | tail -n +6")
        data = stdout.read() + stderr.read()
        client.close()

        data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
        while data:
            update.message.reply_text(data[:4096])
            data = data[4096:]
        return ConversationHandler.END
    
    client = linux_conn()
    stdin, stdout, stderr = client.exec_command('dpkg -s ' +user_input)
    data = stdout.read() + stderr.read()
    client.close()

    data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def get_lsb(update: Update, context):
    logging.info('User called get_lsb function')
    client = linux_conn()
    stdin, stdout, stderr = client.exec_command('cat /etc/os-release')
    data = stdout.read() + stderr.read()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_uptime(update: Update, context):
    client = linux_conn()
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_df(update: Update, context):
    client = linux_conn()
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read() + stderr.read()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_free(update: Update, context):
    client = linux_conn()
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read() + stderr.read()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_w(update: Update, context):
    client = linux_conn()
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_last(update: Update, context):
    client = linux_conn()
    stdin, stdout, stderr = client.exec_command('last -10')
    data = stdout.read() + stderr.read()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

'''def get_monit(update: Update, context):
    passw = 'P@$$w0rd'
    client = linux_conn()
    channel = client.get_transport().open_session()
    channel.get_pty()
    channel.settimeout(5)
    channel.exec_command('sudo monit summary | grep -v "OK"')
    channel.send(passw+'\n')
    channel.recv_exit_status()
    data = channel.recv(1024)
    channel.close()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t').replace('\\r','')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END'''

def get_critical(update: Update, context):
    load_dotenv()
    password = os.getenv('RM_PASSWORD')
    client = linux_conn()
    channel = client.get_transport().open_session()
    channel.get_pty()
    channel.settimeout(5)
    channel.exec_command('sudo journalctl -p 3 | tail -6')
    channel.send(password+'\n')
    channel.recv_exit_status()
    data = channel.recv(1024)
    channel.close()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t').replace('\\r','') [2:-1]
    delimeter= os.getenv('RM_USER')+':'
    update.message.reply_text(data.split(delimeter)[1])
    return ConversationHandler.END

def get_ps(update: Update, context):
    load_dotenv()
    password = os.getenv('RM_PASSWORD')
    client = linux_conn()
    channel = client.get_transport().open_session()
    channel.get_pty()
    channel.settimeout(5)
    channel.exec_command('sudo ps -eo pid,user,%cpu,%mem,start,time,command')
    channel.send(password+'\n')
    channel.recv_exit_status()
    data = channel.recv(81920)
    channel.close()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t').replace('\\r','') [2:-1]
    while data:
        update.message.reply_text(data[:4096])
        data = data[4096:]
    return ConversationHandler.END

def get_ss(update: Update, context):
    load_dotenv()
    password = os.getenv('RM_PASSWORD')
    client = linux_conn()
    channel = client.get_transport().open_session()
    channel.get_pty()
    channel.settimeout(5)
    channel.exec_command('sudo ss -tnlp')
    channel.send(password+'\n')
    channel.recv_exit_status()
    data = channel.recv(81920)
    channel.close()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t').replace('\\r','') [2:-1]
    while data:
        update.message.reply_text(data[:4096])
        data = data[4096:]
    return ConversationHandler.END

def get_services(update: Update, context):
    client = linux_conn()
    stdin, stdout, stderr = client.exec_command('systemctl --type=service --state=running | head -n -7 | cut -d" " -f1 | tail -n +2')
    data = stdout.read() + stderr.read()
    client.close()
    
    data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
    while data:
        update.message.reply_text(data[:4096])
        data = data[4096:]
    return ConversationHandler.END

def repl_logs(update: Update, context):
    #load_dotenv()
    #password = os.getenv('RM_PASSWORD')
    #client = linux_conn()
    #channel = client.get_transport().open_session()
    #channel.get_pty()
    #channel.settimeout(5)
    #channel.exec_command('sudo cat /var/log/postgresql/postgresql-13-main.log ')
    #channel.send(password+'\n')
    #channel.recv_exit_status()
    #data = channel.recv(81920)
    #channel.close()
    #client.close()
    
    #data = str(data).replace('\\n','\n').replace('\\t', '\t').replace('\\r','') [2:-1]
    CONTAINER_RUN = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)
    if CONTAINER_RUN:
        print('CONT')
        data = Path('/logs/postgresql.log').read_text()
        while data:
            update.message.reply_text(data[:4096])
            data = data[4096:]
        return ConversationHandler.END
    
    client = linux_conn_logs()
    stdin, stdout, stderr = client.exec_command('cat /var/log/postgresql/postgresql-13-main.log')
    data = stdout.read() + stderr.read()
    client.close()

    data = str(data).replace('\\n','\n').replace('\\t', '\t')[2:-1]
    while data:
        update.message.reply_text(data[:4096])
        data = data[4096:]
    return ConversationHandler.END

def linux_conn():
    load_dotenv()
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    user = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, user, password)
    return client

def linux_conn_logs():
    load_dotenv()
    host = os.getenv('DB_HOST')
    port = '22'
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, user, password)
    return client

def db_conn():
    load_dotenv()
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_DATABASE')
    CONTAINER_RUN = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)
    if CONTAINER_RUN:
        host = os.getenv('DB_NET_HOST')
    try:
        connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
        #print(psycopg2.extensions.ConnectionInfo(connection).dbname)
    except (Exception, Error) as error:
        result = error
    else:
        result = connection
    return result

def get_emails(update: Update, context):
    conn = db_conn()
    if isinstance(conn, psycopg2.OperationalError):
        update.message.reply_text('Some Error was acuired')
        return ConversationHandler.END
    data = _get_emails_(conn)
    while data:
        update.message.reply_text(data[:4096])
        data = data[4096:]
    return ConversationHandler.END

def _get_emails_(conn):
    data=''
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM emails;")
    _data_ = cursor.fetchall()
    for r in _data_:
        data += r[0]
        data += '\n'
    cursor.close()
    conn.close()
    return data[:-1]

def get_phones(update: Update, context):
    conn = db_conn()
    if isinstance(conn, psycopg2.OperationalError):
        update.message.reply_text('Some Error was acuired')
        return ConversationHandler.END
    data = _get_phones_(conn)
    while data:
        update.message.reply_text(data[:4096])
        data = data[4096:]
    return ConversationHandler.END

def _get_phones_(conn):
    data=''
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM phones;")
    _data_ = cursor.fetchall()
    for r in _data_:
        data += r[0]
        data += '\n'
    cursor.close()
    conn.close()
    return data[:-1]

def main():
    load_dotenv()
    token = os.getenv('TOKEN')
    updater = Updater(token, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Phone NUmbers Handler
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone', findPhoneNumbersCommand)],
        states={
            'find_phone': [MessageHandler(Filters.text & ~Filters.command, find_phone)],
            'add_phones': [MessageHandler(Filters.text & ~Filters.command, add_phones)]
        },
        fallbacks=[]
    )

	# email  Handler
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'add_emails': [MessageHandler(Filters.text & ~Filters.command, add_emails)]
        },
        fallbacks=[]
    )	
	# password_verify  Handler
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )	
    # apt
    convHandlerGetAptInfo = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', GetAptCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", get_lsb))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_last))
#   dp.add_handler(CommandHandler("get_monit", get_monit))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phones))
    dp.add_handler(convHandlerGetAptInfo)
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
    

