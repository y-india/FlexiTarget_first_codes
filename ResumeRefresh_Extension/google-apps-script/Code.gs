const USERS_SHEET = 'Users';
const SUBMISSIONS_SHEET = 'Submissions';
const DRIVE_FOLDER_ID = 'PASTE_YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE';

function doGet() {
  return json({ ok: true, service: 'ResumeRefresh', status: 'online' });
}

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) return json({ok:false,error:'Empty request body.'});
    const body = JSON.parse(e.postData.contents);
    if (body.action === 'register_user') return registerUser(body.user || {});
    if (body.action === 'submit_job') return submitJob(body);
    return json({ok:false,error:'Unknown action.'});
  } catch (error) {
    return json({ok:false,error:error.message || 'Server error.'});
  }
}

function registerUser(user) {
  if (!user.id || !user.name || !user.gmail) return json({ok:false,error:'Missing account fields.'});
  const gmail=String(user.gmail).trim().toLowerCase();
  if (!/^[a-zA-Z0-9._%+-]+@gmail\.com$/i.test(gmail)) return json({ok:false,error:'Only valid Gmail addresses are accepted.'});

  const sheet=getOrCreateSheet(USERS_SHEET,['User ID','Name','Gmail','Created At','Last Used']);
  const values=sheet.getDataRange().getValues();
  for (let i=1;i<values.length;i++) {
    const existingId=String(values[i][0]||'');
    const existingGmail=String(values[i][2]||'').trim().toLowerCase();
    if (existingId===String(user.id) || existingGmail===gmail) {
      const finalId=existingId || String(user.id);
      sheet.getRange(i+1,1,1,5).setValues([[finalId,String(user.name).trim(),gmail,values[i][3]||new Date(),new Date()]]);
      return json({ok:true,userId:finalId,existing:true});
    }
  }
  sheet.appendRow([String(user.id),String(user.name).trim(),gmail,user.createdAt||new Date(),new Date()]);
  return json({ok:true,userId:String(user.id),existing:false});
}

function submitJob(body) {
  const userId=String(body.userId||'').trim();
  const name=String(body.name||'').trim();
  const gmail=String(body.gmail||'').trim().toLowerCase();
  const jobDescription=String(body.jobDescription||'').trim();
  const resume=body.resume||{};
  if (!userId||!name||!gmail) return json({ok:false,error:'User information is missing.'});
  if (!jobDescription) return json({ok:false,error:'Job description is empty.'});
  if (!resume.name||!resume.base64) return json({ok:false,error:'Resume file is missing.'});

  const driveResult=saveResumeToDrive_(resume,userId);
  const sheet=getOrCreateSheet(SUBMISSIONS_SHEET,[
    'Timestamp','User ID','Name','Gmail','Job Description','Resume File Name',
    'Resume Drive Link','Drive File ID','Original Resume Text','Personalized Resume','Changes'
  ]);

  sheet.appendRow([
    new Date(),userId,name,gmail,jobDescription,resume.name,driveResult.url,driveResult.fileId,
    String(body.originalResumeText||''),String(body.personalizedResume||''),String(body.changes||'')
  ]);
  touchUser_(userId);
  return json({ok:true,saved:true,resumeUrl:driveResult.url,fileId:driveResult.fileId});
}

function saveResumeToDrive_(resume,userId) {
  if (DRIVE_FOLDER_ID.includes('PASTE_YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE')) throw new Error('Drive folder is not configured.');
  const bytes=Utilities.base64Decode(String(resume.base64));
  const blob=Utilities.newBlob(bytes,String(resume.mimeType||'application/octet-stream'),makeSafeFileName_(userId+'_'+resume.name));
  const folder=DriveApp.getFolderById(DRIVE_FOLDER_ID);
  const file=folder.createFile(blob);
  return {fileId:file.getId(),url:'https://drive.google.com/file/d/'+file.getId()+'/view'};
}

function touchUser_(userId) {
  const sheet=getOrCreateSheet(USERS_SHEET,['User ID','Name','Gmail','Created At','Last Used']);
  const values=sheet.getDataRange().getValues();
  for (let i=1;i<values.length;i++) if (String(values[i][0]||'')===userId) { sheet.getRange(i+1,5).setValue(new Date()); return; }
}

function getOrCreateSheet(name,headers) {
  const ss=SpreadsheetApp.getActiveSpreadsheet();
  let sheet=ss.getSheetByName(name);
  if (!sheet) sheet=ss.insertSheet(name);
  if (sheet.getLastRow()===0) { sheet.appendRow(headers); sheet.setFrozenRows(1); }
  return sheet;
}

function makeSafeFileName_(name) {
  return String(name).replace(/[\\/:*?"<>|#%{}~&]/g,'_').slice(0,180);
}

function json(data) {
  return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON);
}
