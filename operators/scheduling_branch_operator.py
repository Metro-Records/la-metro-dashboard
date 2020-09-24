from airflow.operators.branch_operator import BaseBranchOperator
from croniter import croniter


class SchedulingBranchOperator(BaseBranchOperator):
    def _in_support_window(self, timestamp):
        '''
        Support window:

        UTC: 9:00 pm Friday to 5:50 am Saturday
        CST: 3:00 pm Friday to 11:50 pm Friday
        CDT: 4:00 pm Friday to 12:50 am Saturday
        '''
        # Monday is 0, Sunday is 6:
        # https://docs.python.org/3.7/library/datetime.html#datetime.date.weekday
        FRIDAY = 4
        SATURDAY = 5

        friday_night = timestamp.weekday() == FRIDAY and timestamp.hour >= 21
        saturday_morning = timestamp.weekday() == SATURDAY and timestamp.hour <= 5

        return friday_night or saturday_morning

    def _index_in_interval(self, interval, timestamp):
        minutes, *_ = croniter(interval).expanded
        return minutes.split(',').index(timestamp.minute)

    def choose_branch(self, context):
        interval = context['dag'].schedule_interval
        timestamp = context['execution_date']

        if self._in_support_window(timestamp):
            index_in_interval = self._index_in_interval(interval, timestamp)

            if index_in_interval == 0:
                return 'fast_full_scrape'

            elif index_in_interval == 1:
                return 'no_scrape'

            elif index_in_interval in (2, 3):
                return 'broader_scrape'

        return 'regular_scrape'
