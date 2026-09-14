import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from ugaforce_hr import security

class HRAuthTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'UGAFORCE_HR_SHARED_ADMIN_USERNAME':'owner@example.com','UGAFORCE_HR_SHARED_AUTH_URL':'https://identity.example'})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_other_staff_keep_local_authentication(self):
        with patch.object(security,'authenticate_local',return_value={'user':'staff'}):
            self.assertEqual(security.authenticate('staff','pass'),{'user':'staff'})

    def test_invalid_shared_password_cannot_fall_back_to_old_hr_password(self):
        with patch.object(security,'DATABASE_URL','postgres'), patch('ugaforce_hr.shared_signin.verify_master',side_effect=HTTPException(401,'Invalid credentials')), patch.object(security,'authenticate_local',side_effect=AssertionError('unsafe fallback')):
            with self.assertRaises(HTTPException) as raised:
                security.authenticate('OWNER@example.com','old-password')
            self.assertEqual(raised.exception.status_code,401)

    def test_shared_login_preserves_hr_role(self):
        connection=MagicMock()
        connection.__enter__.return_value=connection
        cursor=connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value=('user-id','owner@example.com','HR_MANAGER',True,None)
        with patch.object(security,'DATABASE_URL','postgres'), patch('ugaforce_hr.shared_signin.verify_master',return_value=True), patch.object(security.psycopg2,'connect',return_value=connection), patch.object(security,'issue_session',return_value=('hr_session',123)):
            result=security.authenticate('owner@example.com','example-code')
        self.assertEqual(result['user']['role'],'HR_MANAGER')
        self.assertEqual(result['token'],'hr_session')

    def test_disabled_hr_account_stays_disabled(self):
        connection=MagicMock()
        connection.__enter__.return_value=connection
        connection.cursor.return_value.__enter__.return_value.fetchone.return_value=('id','owner@example.com','HR_ADMIN',False,None)
        with patch.object(security,'DATABASE_URL','postgres'), patch('ugaforce_hr.shared_signin.verify_master',return_value=True), patch.object(security.psycopg2,'connect',return_value=connection):
            with self.assertRaises(HTTPException) as raised:
                security.authenticate('owner@example.com','example-code')
        self.assertEqual(raised.exception.status_code,403)
