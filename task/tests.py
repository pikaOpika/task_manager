from django.test import TestCase
from django.urls import reverse

from task.models import TaskType, Task, Worker, Position, Project
from task.forms import WorkerUpdateForm


class TaskTypeModelTest(TestCase):
    def test_str_returns_name(self):
        task_type = TaskType.objects.create(name="Test")
        self.assertEqual(str(task_type), "Test")

    def test_ordering(self):
        TaskType.objects.create(name="Backend")
        TaskType.objects.create(name="Agile")
        task_type = TaskType.objects.all()
        self.assertEqual(task_type[0].name, "Agile")

class TaskModelTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(
            name="test",
            description="test description",
            deadline="2012-12-12",
            task_type=TaskType.objects.create(name="Type test"),
        )
        self.task.assignees.add(Worker.objects.create_user("username", "user@gmail.com", "Yhnujm123"))
    
    def test_str_returns_name(self):
        self.assertEqual(str(self.task), self.task.name)
    
    def test_default_is_completed(self):
        self.assertFalse(self.task.is_completed)
    
    def test_default_priority(self):
        self.assertEqual(self.task.priority, "L")

class TaskListViewTest(TestCase):
    def setUp(self):
        self.user = Worker.objects.create_user(
            username="user",
            password="1234556787"
        )
        self.client.login(username="user", password="1234556787")
        self.task = Task.objects.create(
            name="test",
            description="test description",
            deadline="2012-12-12",
            task_type=TaskType.objects.create(name="Type test"),
        )
        self.task.assignees.add(self.user)

    def test_page_accesible(self):
        res = self.client.get(reverse("task:task-list"))
        self.assertEqual(res.status_code, 200)
    
    def test_unauthorised_page_accesible(self):
        self.client.logout()
        res = self.client.get(reverse("task:task-list"))
        self.assertEqual(res.status_code, 200)

    def test_user_correct_template(self):
        res = self.client.get(reverse("task:task-list"))
        self.assertTemplateUsed(res, "task/task_list.html")
    
    def test_login_required_for_detail(self):
        self.client.logout()
        res = self.client.get(reverse("task:task-detail", kwargs={"slug": self.task.slug}))
        self.assertEqual(res.status_code, 302)

class TaskCreateViewTest(TestCase):
    def setUp(self):
        worker = Worker.objects.create_user(username="wor", password="1234")
        task_type = TaskType.objects.create(name="test")
        self.data = {
            "name": "test",
            "description": "test ",
            "deadline": "2012-12-12",
            "priority": "L",
            "task_type": task_type.id,
            "assignees": worker.id,
        }
        
        self.client.login(username="wor", password="1234")

    def test_get_form_page(self):
        res = self.client.get(reverse("task:task-create"))
        self.assertEqual(res.status_code, 200)
    
    def test_create_task_success(self):
        res = self.client.post(reverse("task:task-create"), data=self.data)
        self.assertRedirects(res, reverse("task:task-list"))
        self.assertTrue(Task.objects.filter(name="test").exists())
    
    def test_create_requires_login(self):
        self.client.logout()
        res = self.client.post(reverse("task:task-create"), data=self.data)
        self.assertEqual(res.status_code, 302)

class TaskUpdateViewTest(TestCase):
    def setUp(self):
        worker = Worker.objects.create_user(username="anton", password="1234")
        task_type = TaskType.objects.create(name="test")
        self.client.login(username="anton", password="1234")
        self.task = Task.objects.create(
            name="test",
            description="test",
            deadline="1200-12-12",
        )
        self.data = {
            "name": "test1",
            "description": "test ",
            "deadline": "2012-12-12",
            "priority": "L",
            "task_type": task_type.id,
            "assignees": worker.id,
        }
    
    def test_get_update_page(self):
        res = self.client.get(reverse("task:task-update", kwargs={"slug": self.task.slug}))
        self.assertEqual(res.status_code, 200)
    
    def test_update_task_success(self):
        res = self.client.post(reverse("task:task-update", kwargs={"slug": self.task.slug}), data=self.data)
        self.assertRedirects(res, reverse("task:task-detail", kwargs={"slug": self.task.slug}))
    
    def test_update_task_changes_name(self):
        self.client.post(reverse("task:task-update", kwargs={"slug": self.task.slug}), data=self.data)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "test1")

    
class WorkerUpdateFormTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="test")

    def test_valid_form(self):
        form = WorkerUpdateForm({
            "username": "hello",
            "position": self.position.id,
        }
        )
        self.assertTrue(form.is_valid())
    
    def test_username_required(self):
        form = WorkerUpdateForm(
            {"username": None}
        )
        self.assertFalse(form.is_valid())


class WorkerListViewTest(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create_user(username="test", password="1234")
        self.client.login(username="test", password="1234")
    
    def test_worker_list_authenticated(self):
        res = self.client.get(reverse("task:worker-list"))
        self.assertEqual(res.status_code, 200)
    
    def test_worker_list_annonymous(self):    
        self.client.logout()
        res = self.client.get(reverse("task:worker-list"))
        self.assertEqual(res.status_code, 200)
    
    def test_correct_template(self):
        res = self.client.get(reverse("task:worker-list"))
        self.assertTemplateUsed(res, "task/worker_list.html")
    
    def test_filter_search_by_username(self):
        self.worker1 = Worker.objects.create_user(username="alice", password="1234")
        res = self.client.get(reverse("task:worker-list") + "?username=alice")
        self.assertIn(self.worker1, res.context["worker_list"])
        self.assertNotIn(self.worker, res.context["worker_list"])

class WorkerUpdateViewTest(TestCase):
    def setUp(self):
        self.worker1 = Worker.objects.create_user(username="v1", password="1")
        self.worker2 = Worker.objects.create_user(username="v2", password="2")
        self.client.login(username="v1", password="1")
    
    def test_owner_can_udpate(self):
        res = self.client.post(reverse("task:worker-update", kwargs={"slug": self.worker1.slug}), data={"username": "w"})
        self.assertEqual(res.status_code, 302)
        self.worker1.refresh_from_db()
        self.assertRedirects(res, reverse("task:worker-detail", kwargs={"slug": self.worker1.slug}))

    def test_other_user_cannot_update(self):
        res = self.client.post(reverse("task:worker-update", kwargs={"slug": self.worker2.slug}))
        self.assertEqual(res.status_code, 403)