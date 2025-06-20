from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from app.database.models import UserReport, UserSuspension, UserData, ReportPriority


class ReportService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_report(
        self,
        reporter_id: int,
        reported_user_id: int,
        priority: ReportPriority,
        reason: str
    ) -> UserReport:
        """
        Create a new user report and check if the reported user should be suspended
        """
      
        if reporter_id == reported_user_id:
            raise ValueError("Users cannot report themselves")
        
        if not self.db.query(UserData).filter(UserData.id == reported_user_id).first():
            raise ValueError("Reported user does not exist")
        if self._is_user_suspended(reporter_id):
            raise ValueError("Suspended users cannot submit reports")
        #to be checked
 
        recent_report = self.db.query(UserReport).filter(
            UserReport.reporter_id == reporter_id,
            UserReport.reported_user_id == reported_user_id,
            UserReport.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).first()
        
        if recent_report:
            raise ValueError("You have already reported this user recently. Please wait before submitting another report.")
        
        # Create the report
        report = UserReport(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            priority=priority,
            reason=reason
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        # Check if user should be suspended
        self._check_for_suspension(reported_user_id)
        
        return report
    
    def _check_for_suspension(self, user_id: int) -> Optional[UserSuspension]:


        total_score, critical_count = self._calculate_report_score(user_id)
        
        # If score reaches threshold (equivalent to 20 low-priority reports)
        if total_score >= 20:
            
            active_suspension = self._get_active_suspension(user_id) #check if user is already suspended
            
            if not active_suspension: 
                return self._suspend_user(
                    user_id=user_id,
                    reason=f"Automatically suspended due to {total_score} report points "
                           f"({critical_count} critical reports)",
                    days=self._calculate_suspension_duration(critical_count)
                )
        return None
    
    def _calculate_report_score(self, user_id: int) -> Tuple[int, int]:

        unresolved_reports = self.db.query(UserReport).filter(
            UserReport.reported_user_id == user_id,
            UserReport.is_resolved == False
        ).all()
        
        total_score = 0
        critical_count = 0
        
        for report in unresolved_reports:
            if report.priority == ReportPriority.CRITICAL:
                total_score += 5
                critical_count += 1
            elif report.priority == ReportPriority.HIGH:
                total_score += 3
            elif report.priority == ReportPriority.MEDIUM:
                total_score += 2
            else:
                total_score += 1
        print(f"Total score for user {user_id}: {total_score}, Critical reports: {critical_count}")      
        return total_score,critical_count
        
       
    
    def _calculate_suspension_duration(self, critical_count: int) -> int:
        """
        Calculate suspension duration based on severity of reports
        """
        if critical_count >= 3:
            return 30  # 30 days for users with 3+ critical reports
        elif critical_count >= 1:
            return 15  # 15 days for users with 1-2 critical reports
        return 7  # 7 days for users with only low/medium priority reports
    
    def _suspend_user(self, user_id: int, reason: str, days: int) -> UserSuspension:
        """
        Suspend a user account for the specified number of days
        """
        suspension = UserSuspension(
            user_id=user_id,
            suspension_reason=reason,
            suspension_start=datetime.utcnow(),
            suspension_end=datetime.utcnow() + timedelta(days=days),
            is_active=True 
        )
        
        # Lock the user's account
        user = self.db.query(UserData).filter(UserData.id == user_id).first()
        if user:
            user.is_locked = True
        
        self.db.add(suspension)
        self.db.commit()
        return suspension
    

  
    def get_reports_made_by_user(self, user_id: int, resolved: Optional[bool] = None) -> List[UserReport]:
        """
        Get all reports made by a specific user
        """
        query = self.db.query(UserReport).filter(UserReport.reporter_id == user_id)
        
        if resolved is not None:
            query = query.filter(UserReport.is_resolved == resolved)
            
        return query.order_by(UserReport.created_at.desc()).all()
    
    def _get_active_suspension(self, user_id: int) -> Optional[UserSuspension]:
        """
        Check if a user currently has an active suspension
        """
        return self.db.query(UserSuspension).filter(
            UserSuspension.user_id == user_id,
            UserSuspension.is_active == True
        ).first()
    
    def _is_user_suspended(self, user_id: int) -> bool:
        """
        Check if a user is currently suspended
        """
        return self._get_active_suspension(user_id) is not None #teraga3 kol el active beta3hom b true
    
    def get_user_report_stats(self, user_id: int) -> dict:
        """
        Get statistics about a user's reports
        """
        reports = self.db.query(UserReport).filter(
            UserReport.reported_user_id == user_id,
            UserReport.is_resolved == False
        ).all()
        
        stats = {
            'total_reports': len(reports),
            'critical': sum(1 for r in reports if r.priority == ReportPriority.CRITICAL),
            'high': sum(1 for r in reports if r.priority == ReportPriority.HIGH),
            'medium': sum(1 for r in reports if r.priority == ReportPriority.MEDIUM),
            'low': sum(1 for r in reports if r.priority == ReportPriority.LOW),
            'score': self._calculate_report_score(user_id)[0],
            'is_suspended': self._is_user_suspended(user_id)
        }
        
        if stats['is_suspended']:
            suspension = self._get_active_suspension(user_id)
            stats['suspension_end'] = suspension.suspension_end
            stats['suspension_reason'] = suspension.suspension_reason
        
        return stats
    
    def lift_suspension(self, user_id: int, lifter_id: Optional[int] = None) -> Optional[UserSuspension]:
        
        suspension = self._get_active_suspension(user_id)
        if not suspension:
            return None
        
        suspension.is_active = False
        suspension.lifted_at = datetime.utcnow()
        if lifter_id:
            suspension.lifted_by = lifter_id
        

        # Unlock the user's account
        user = self.db.query(UserData).filter(UserData.id == user_id).first()
        if user:
            user.is_locked = False
        
        self.db.commit()
        return suspension

    
    def check_expired_suspensions(self) -> List[UserSuspension]:
       
        expired_suspensions = self.db.query(UserSuspension).filter(
            UserSuspension.is_active == True,
            UserSuspension.suspension_end <= datetime.utcnow()
        ).all()
        
        lifted = []
        for suspension in expired_suspensions:
            print(f"Lifting suspension for user {suspension.user_id} due to expiration")
            lifted.append(self.lift_suspension(suspension.user_id))
        self.db.commit()
        return lifted
