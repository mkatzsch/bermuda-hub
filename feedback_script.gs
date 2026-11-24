/**
 * Bermuda Hub: bug report receiver. Takes the notes sent by the Hub's Report button, and the Hub's own error
 * reports, and writes one row for each to the "Reports" tab of the Google Sheet this script is attached to.
 * A note from a person also sends one email to the owner of the sheet.
 *
 * Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
 * Version: 1.0
 * Last Updated: 2026-11-24
 *
 * Change Log
 *   1.0 2026-11-24  First release.
 *
 * Depends on: a Google Sheet (this script lives inside it: Extensions, then Apps Script) and the web app
 * address it is given when deployed, which goes in events/data/feedback.json as "url". This file is a copy
 * kept with the code. The copy that runs is the one pasted into Google.
 *
 * Set up (once, about ten minutes, on the laptop):
 *   1. Go to sheets.new and name the sheet "Bermuda Hub reports". Keep it private (do not share it).
 *   2. Extensions, then Apps Script. Delete what is there, paste this whole file, and press Save.
 *   3. Pick "setup" in the function list at the top and press Run. Google asks for permission: allow it.
 *      The sheet now has a "Reports" tab with its headings.
 *   4. Deploy, then New deployment. Type: Web app. Execute as: Me. Who has access: Anyone. Press Deploy.
 *   5. Copy the Web app URL (it ends in /exec) into events/data/feedback.json as "url", then run build_now.bat.
 * After a change to this script: Deploy, Manage deployments, edit, Version: New version. The address stays the same.
 *
 * Safeguards: nothing sent here is ever shown on the Hub. Text is cut to length, control characters are
 * removed, and a leading = + - or @ is removed so a note can never run as a spreadsheet formula. No more than
 * MAX_PER_HOUR rows are written in an hour and no more than MAX_EMAILS_PER_DAY emails are sent in a day.
 */
var SHEET = 'Reports';
var HEAD = ['When', 'Status', 'Kind', 'Page', 'Card', 'Message', 'Contact', 'Build', 'App', 'Screen', 'Phone'];
var MAX_PER_HOUR = 60;
var MAX_EMAILS_PER_DAY = 20;

function clean(v, n) {
  return String(v == null ? '' : v).replace(/[\u0000-\u001f\u007f]+/g, ' ').replace(/^[=+\-@\s]+/, '').trim().slice(0, n);
}

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET) || ss.insertSheet(SHEET);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEAD);
    sh.setFrozenRows(1);
  }
  return sh;
}

// Adds one to a counter kept for a short while and says whether it is still under the limit.
function under_(key, limit, seconds) {
  var cache = CacheService.getScriptCache();
  var n = Number(cache.get(key) || 0);
  if (n >= limit) return false;
  cache.put(key, String(n + 1), seconds);
  return true;
}

function doPost(e) {
  var out = ContentService.createTextOutput('ok');
  try {
    var raw = (e && e.postData && e.postData.contents) || '';
    if (!raw || raw.length > 4000) return out;
    var d = JSON.parse(raw);
    if (d.website) return out;  // the hidden field that only a robot fills in
    var kind = d.kind === 'auto' ? 'auto' : 'user';
    var msg = clean(d.msg, 600);
    if (msg.length < 5) return out;
    if (!under_('h' + Math.floor(Date.now() / 3600000), MAX_PER_HOUR, 7200)) return out;
    var contact = clean(d.contact, 80), page = clean(d.page, 40), card = clean(d.card, 60), build = clean(d.build, 40);
    var lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      sheet_().appendRow([new Date(), 'new', kind, page, card, msg, contact, build, clean(d.app, 12), clean(d.screen, 12), clean(d.ua, 160)]);
    } finally {
      lock.releaseLock();
    }
    if (kind === 'user' && under_('d' + Math.floor(Date.now() / 86400000), MAX_EMAILS_PER_DAY, 90000)) {
      MailApp.sendEmail(Session.getEffectiveUser().getEmail(), 'Bermuda Hub report: ' + msg.slice(0, 60),
        msg + '\n\nPage: ' + page + '\nCard: ' + card + '\nBuild: ' + build + '\nContact: ' + (contact || 'none given') +
        '\n\nThe full list is in the Bermuda Hub reports sheet.');
    }
  } catch (err) {
    // a bad report is dropped: the sender always gets the same plain answer
  }
  return out;
}

function doGet() {
  return ContentService.createTextOutput('Bermuda Hub report receiver is running.');
}

// Run this once from the editor: it makes the Reports tab and asks for the permissions the script needs.
function setup() {
  sheet_();
  MailApp.getRemainingDailyQuota();
}
