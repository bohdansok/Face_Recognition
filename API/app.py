import os
from flask import Flask, request, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import frapi
from waitress import serve
from app_conf import * # import app configuration



# Flask app config - start
frapp = Flask(__name__)
frapp.config['THREADED'] = True
frapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
frapp.config['SECRET_KEY'] = os.urandom(24)
frapp.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days = 3)
# Flask app config - end



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@frapp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        dir_comment = ""
        dir_comment = request.form.get("dir_comment")
        if not dir_comment:
            dir_comment = "Опис не надано"
        tol = request.form.get("var_tol")
        if not tol:
            tolerance = default_tol
        else:
            try:
                tol = float(str(tol).replace(",", "."))
                if 0.0 < tol < 1.0:
                    tolerance = tol
                else:
                    tolerance = default_tol
            except:
                tolerance = default_tol
                
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            user_dir = os.path.join(frapp.config['UPLOAD_FOLDER'], str(datetime.now()).replace(
                ":", "").replace(
                    "-", "").replace(" ", "") + "(" + f"{request.environ['REMOTE_ADDR']}" + ")" )
            if not os.path.exists(user_dir):
                os.mkdir(user_dir)
            file.save(os.path.join(user_dir, filename))
            print("[INFO] User IP:", request.environ['REMOTE_ADDR'])
            user_ip = request.environ['REMOTE_ADDR']
            result, msg, fullpath_rep = frapi.API(user_dir, user_ip,
                                                  frapp.config['UPLOAD_FOLDER'],
                                                  dir_comment,
                                                  tol=tolerance,
                                                  fl_use_dlib=True)
            if result:
                filename = os.path.split(fullpath_rep)[1]
                print(f"[RESULT] {user_ip}", msg)
                return render_template('result.html', msg=msg, filename=filename)
            else:
                print(f"[RESULT] {user_ip}:", msg)
                return render_template('noresult.html', msg=msg)
        else:
            return render_template('noresult.html', msg=f"Допустимі формати зображень: {ALLOWED_EXTENSIONS}")
    return render_template('_index.html')


@frapp.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(directory=frapp.config['UPLOAD_FOLDER'],
                               path=filename,
                               as_attachment=True,
                               mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


print(f"Trying to run FR Server at {LISTEN}")
serve(frapp,
      listen=LISTEN,
      threads=8,
      asyncore_use_poll=True)
print(f"FR Server is stopped at {LISTEN}")
