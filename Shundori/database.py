"""
Database models and session management for the attendance bot using MongoDB.
"""
from datetime import date, datetime, timezone
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from bson import ObjectId


class Column:
    """Column descriptor for MongoDB compatibility with SQLAlchemy-style queries."""
    def __init__(self, name: str):
        self.name = name
    
    def __eq__(self, other):
        return QueryCondition(self.name, 'eq', other)
    
    def __ge__(self, other):
        return QueryCondition(self.name, 'ge', other)
    
    def __le__(self, other):
        return QueryCondition(self.name, 'le', other)
    
    def __gt__(self, other):
        return QueryCondition(self.name, 'gt', other)
    
    def __lt__(self, other):
        return QueryCondition(self.name, 'lt', other)


class QueryCondition:
    """Represents a query condition."""
    def __init__(self, field_name: str, operator: str, value):
        self.field_name = field_name
        self.operator = operator
        self.value = value

load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'attendance_bot')

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_client() -> MongoClient:
    """Get or create MongoDB client."""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client


def get_database() -> Database:
    """Get or create database instance."""
    global _db
    if _db is None:
        client = get_client()
        _db = client[DATABASE_NAME]
    return _db


def get_collection(collection_name: str) -> Collection:
    """Get a collection from the database."""
    db = get_database()
    return db[collection_name]


# Collection names
USERS_COLLECTION = 'users'
ATTENDANCE_COLLECTION = 'attendance_records'
FINES_COLLECTION = 'fines'
SETTINGS_COLLECTION = 'settings'


class User:
    """Telegram user model (MongoDB document)."""
    
    # Column definitions for query compatibility
    telegram_id = Column('telegram_id')
    username = Column('username')
    full_name = Column('full_name')
    created_at = Column('created_at')
    is_active = Column('is_active')
    
    def __init__(self, telegram_id: int, username: str = None, full_name: str = None, 
                 created_at: datetime = None, is_active: bool = True, _id: ObjectId = None):
        self._id = _id
        self.telegram_id = telegram_id
        self.username = username
        self.full_name = full_name
        self.created_at = created_at or datetime.now(timezone.utc)
        self.is_active = is_active
    
    @property
    def id(self):
        """Get MongoDB _id as string for compatibility."""
        return str(self._id) if self._id else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        doc = {
            'telegram_id': self.telegram_id,
            'username': self.username,
            'full_name': self.full_name,
            'created_at': self.created_at,
            'is_active': self.is_active
        }
        if self._id:
            doc['_id'] = self._id
        return doc
    
    @classmethod
    def from_dict(cls, doc: Dict[str, Any]) -> 'User':
        """Create User from MongoDB document."""
        # Handle ObjectId conversion
        _id = doc.get('_id')
        if _id and not isinstance(_id, ObjectId):
            try:
                _id = ObjectId(_id)
            except:
                pass
        
        # Handle datetime conversion
        created_at = doc.get('created_at')
        if created_at and isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                try:
                    from dateutil import parser
                    created_at = parser.parse(created_at)
                except:
                    created_at = datetime.now(timezone.utc)
        elif not created_at:
            created_at = datetime.now(timezone.utc)
        elif isinstance(created_at, datetime):
            # Already a datetime, ensure it's timezone-aware
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
        
        return cls(
            _id=_id,
            telegram_id=doc['telegram_id'],
            username=doc.get('username'),
            full_name=doc.get('full_name'),
            created_at=created_at,
            is_active=doc.get('is_active', True)
        )
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class AttendanceRecord:
    """Daily attendance record (MongoDB document)."""
    
    # Column definitions for query compatibility
    user_id = Column('user_id')
    date = Column('date')
    status = Column('status')
    timestamp = Column('timestamp')
    created_at = Column('created_at')
    
    def __init__(self, user_id: str, date: date, status: str, 
                 timestamp: datetime = None, created_at: datetime = None, _id: ObjectId = None):
        self._id = _id
        self.user_id = user_id
        self.date = date
        self.status = status  # 'present', 'absent', 'late'
        self.timestamp = timestamp
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def get_id(self):
        """Get MongoDB _id as string for compatibility."""
        return str(self._id) if self._id else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        # Convert date to datetime for MongoDB (MongoDB doesn't support Python date objects)
        date_val = self.date
        if isinstance(date_val, date) and not isinstance(date_val, datetime):
            date_val = datetime.combine(date_val, datetime.min.time()).replace(tzinfo=timezone.utc)
        
        doc = {
            'user_id': str(self.user_id),  # Ensure user_id is always a string
            'date': date_val,
            'status': self.status,
            'created_at': self.created_at
        }
        if self.timestamp:
            timestamp = self.timestamp
            if timestamp.tzinfo is None:
                # Assume naive timestamps are already UTC
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            else:
                timestamp = timestamp.astimezone(timezone.utc)
            doc['timestamp'] = timestamp
        if self._id:
            doc['_id'] = self._id
        return doc
    
    @classmethod
    def from_dict(cls, doc: Dict[str, Any]) -> 'AttendanceRecord':
        """Create AttendanceRecord from MongoDB document."""
        # Handle ObjectId conversion
        _id = doc.get('_id')
        if _id and not isinstance(_id, ObjectId):
            try:
                _id = ObjectId(_id)
            except:
                pass
        
        # Handle date conversion
        date_val = doc['date']
        if isinstance(date_val, str):
            try:
                date_val = datetime.strptime(date_val, '%Y-%m-%d').date()
            except:
                date_val = datetime.fromisoformat(date_val).date()
        elif isinstance(date_val, datetime):
            date_val = date_val.date()
        
        # Handle timestamp conversion
        timestamp = doc.get('timestamp')
        if timestamp and isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                try:
                    from dateutil import parser
                    timestamp = parser.parse(timestamp)
                except:
                    timestamp = None
        elif timestamp and isinstance(timestamp, datetime):
            # Already a datetime, ensure it's timezone-aware
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        # Handle created_at conversion
        created_at = doc.get('created_at')
        if created_at and isinstance(created_at, str):
            try:
                from dateutil import parser
                created_at = parser.parse(created_at)
            except:
                created_at = datetime.now(timezone.utc)
        elif not created_at:
            created_at = datetime.now(timezone.utc)
        
        return cls(
            _id=_id,
            user_id=str(doc['user_id']),  # Ensure user_id is always a string
            date=date_val,
            status=doc['status'],
            timestamp=timestamp,
            created_at=created_at
        )
    
    def __repr__(self):
        return f"<AttendanceRecord(user_id={self.user_id}, date={self.date}, status={self.status})>"


class Fine:
    """Fine record for late/absent members (MongoDB document)."""
    
    # Column definitions for query compatibility
    user_id = Column('user_id')
    date = Column('date')
    amount = Column('amount')
    created_at = Column('created_at')
    id = Column('_id')
    
    def __init__(self, user_id: str, date: date, amount: float, 
                 created_at: datetime = None, _id: ObjectId = None):
        self._id = _id
        self.user_id = user_id
        self.date = date
        self.amount = amount
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def get_id(self):
        """Get MongoDB _id as string for compatibility."""
        return str(self._id) if self._id else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        # Convert date to datetime for MongoDB (MongoDB doesn't support Python date objects)
        date_val = self.date
        if isinstance(date_val, date) and not isinstance(date_val, datetime):
            date_val = datetime.combine(date_val, datetime.min.time()).replace(tzinfo=timezone.utc)
        
        doc = {
            'user_id': str(self.user_id),  # Ensure user_id is always a string
            'date': date_val,
            'amount': self.amount,
            'created_at': self.created_at
        }
        if self._id:
            doc['_id'] = self._id
        return doc
    
    @classmethod
    def from_dict(cls, doc: Dict[str, Any]) -> 'Fine':
        """Create Fine from MongoDB document."""
        # Handle ObjectId conversion
        _id = doc.get('_id')
        if _id and not isinstance(_id, ObjectId):
            try:
                _id = ObjectId(_id)
            except:
                pass
        
        # Handle date conversion
        date_val = doc['date']
        if isinstance(date_val, str):
            try:
                date_val = datetime.strptime(date_val, '%Y-%m-%d').date()
            except:
                date_val = datetime.fromisoformat(date_val).date()
        elif isinstance(date_val, datetime):
            date_val = date_val.date()
        
        # Handle created_at conversion
        created_at = doc.get('created_at')
        if created_at and isinstance(created_at, str):
            try:
                from dateutil import parser
                created_at = parser.parse(created_at)
            except:
                created_at = datetime.now(timezone.utc)
        elif not created_at:
            created_at = datetime.now(timezone.utc)
        
        return cls(
            _id=_id,
            user_id=str(doc['user_id']),  # Ensure user_id is always a string
            date=date_val,
            amount=float(doc['amount']),
            created_at=created_at
        )
    
    def __repr__(self):
        return f"<Fine(user_id={self.user_id}, date={self.date}, amount={self.amount})>"


class Settings:
    """Bot settings (MongoDB document)."""
    
    # Column definitions for query compatibility
    key = Column('key')
    value = Column('value')
    updated_at = Column('updated_at')
    
    def __init__(self, key: str, value: str, updated_at: datetime = None, _id: ObjectId = None):
        self._id = _id
        self.key = key
        self.value = value
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def get_id(self):
        """Get MongoDB _id as string for compatibility."""
        return str(self._id) if self._id else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        doc = {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at
        }
        if self._id:
            doc['_id'] = self._id
        return doc
    
    @classmethod
    def from_dict(cls, doc: Dict[str, Any]) -> 'Settings':
        """Create Settings from MongoDB document."""
        # Handle ObjectId conversion
        _id = doc.get('_id')
        if _id and not isinstance(_id, ObjectId):
            try:
                _id = ObjectId(_id)
            except:
                pass
        
        # Handle updated_at conversion
        updated_at = doc.get('updated_at')
        if updated_at and isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            except:
                try:
                    from dateutil import parser
                    updated_at = parser.parse(updated_at)
                except:
                    updated_at = datetime.now(timezone.utc)
        elif not updated_at:
            updated_at = datetime.now(timezone.utc)
        elif isinstance(updated_at, datetime):
            # Already a datetime, ensure it's timezone-aware
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=timezone.utc)
        
        return cls(
            _id=_id,
            key=doc['key'],
            value=doc['value'],
            updated_at=updated_at
        )
    
    def __repr__(self):
        return f"<Settings(key={self.key}, value={self.value})>"


def init_db():
    """Initialize database indexes."""
    db = get_database()
    
    # Create indexes for users collection
    users_col = get_collection(USERS_COLLECTION)
    users_col.create_index('telegram_id', unique=True)
    users_col.create_index('is_active')
    
    # Create indexes for attendance_records collection
    attendance_col = get_collection(ATTENDANCE_COLLECTION)
    attendance_col.create_index([('user_id', 1), ('date', 1)], unique=True)
    attendance_col.create_index('date')
    attendance_col.create_index('user_id')
    
    # Create indexes for fines collection
    fines_col = get_collection(FINES_COLLECTION)
    fines_col.create_index([('user_id', 1), ('date', 1)], unique=True)
    fines_col.create_index('date')
    fines_col.create_index('user_id')
    
    # Create indexes for settings collection
    settings_col = get_collection(SETTINGS_COLLECTION)
    settings_col.create_index('key', unique=True)


@contextmanager
def get_db():
    """
    Database session context manager (for compatibility with existing code).
    Returns a dictionary-like object that mimics SQLAlchemy session behavior.
    """
    class DBSession:
        """Mimics SQLAlchemy session interface for MongoDB."""
        
        def query(self, model_class):
            """Create a query object for the model."""
            return QueryBuilder(model_class)
        
        def add(self, instance):
            """Add instance to be saved (stored in memory for commit)."""
            if not hasattr(self, '_pending_add'):
                self._pending_add = []
            self._pending_add.append(instance)
        
        def delete(self, instance):
            """Delete instance (stored in memory for commit)."""
            if not hasattr(self, '_pending_delete'):
                self._pending_delete = []
            self._pending_delete.append(instance)
        
        def commit(self):
            """Commit pending changes."""
            if hasattr(self, '_pending_add'):
                for instance in self._pending_add:
                    self._save_instance(instance)
                delattr(self, '_pending_add')
            
            if hasattr(self, '_pending_delete'):
                for instance in self._pending_delete:
                    self._delete_instance(instance)
                delattr(self, '_pending_delete')
        
        def refresh(self, instance):
            """Refresh instance from database."""
            if isinstance(instance, User):
                collection = get_collection(USERS_COLLECTION)
                if instance._id:
                    # Ensure _id is ObjectId for query
                    query_id = instance._id
                    if not isinstance(query_id, ObjectId):
                        try:
                            query_id = ObjectId(query_id)
                        except:
                            pass
                    doc = collection.find_one({'_id': query_id})
                elif hasattr(instance, 'telegram_id') and instance.telegram_id:
                    doc = collection.find_one({'telegram_id': instance.telegram_id})
                else:
                    return
                if doc:
                    refreshed = User.from_dict(doc)
                    instance.__dict__.update(refreshed.__dict__)
        
        def _save_instance(self, instance):
            """Save instance to MongoDB."""
            if isinstance(instance, User):
                collection = get_collection(USERS_COLLECTION)
                doc = instance.to_dict()
                # Remove _id from $set operation for updates
                if instance._id:
                    update_doc = {k: v for k, v in doc.items() if k != '_id'}
                    collection.update_one({'_id': instance._id}, {'$set': update_doc})
                else:
                    result = collection.insert_one(doc)
                    instance._id = result.inserted_id
            
            elif isinstance(instance, AttendanceRecord):
                collection = get_collection(ATTENDANCE_COLLECTION)
                doc = instance.to_dict()
                # Use upsert for unique constraint on user_id + date
                if instance._id:
                    update_doc = {k: v for k, v in doc.items() if k != '_id'}
                    collection.update_one({'_id': instance._id}, {'$set': update_doc})
                else:
                    # Try to find existing record first
                    existing = collection.find_one({
                        'user_id': doc['user_id'],
                        'date': doc['date']
                    })
                    if existing:
                        instance._id = existing.get('_id')
                        update_doc = {k: v for k, v in doc.items() if k != '_id'}
                        collection.update_one({'_id': instance._id}, {'$set': update_doc})
                    else:
                        result = collection.insert_one(doc)
                        instance._id = result.inserted_id
            
            elif isinstance(instance, Fine):
                collection = get_collection(FINES_COLLECTION)
                doc = instance.to_dict()
                # Use upsert for unique constraint on user_id + date
                if instance._id:
                    update_doc = {k: v for k, v in doc.items() if k != '_id'}
                    collection.update_one({'_id': instance._id}, {'$set': update_doc})
                else:
                    # Try to find existing record first
                    existing = collection.find_one({
                        'user_id': doc['user_id'],
                        'date': doc['date']
                    })
                    if existing:
                        instance._id = existing.get('_id')
                        update_doc = {k: v for k, v in doc.items() if k != '_id'}
                        collection.update_one({'_id': instance._id}, {'$set': update_doc})
                    else:
                        result = collection.insert_one(doc)
                        instance._id = result.inserted_id
            
            elif isinstance(instance, Settings):
                collection = get_collection(SETTINGS_COLLECTION)
                doc = instance.to_dict()
                if instance._id:
                    collection.update_one({'_id': instance._id}, {'$set': doc})
                else:
                    # Use upsert for settings to handle unique key constraint
                    result = collection.update_one(
                        {'key': instance.key},
                        {'$set': doc},
                        upsert=True
                    )
                    # Get the _id after upsert
                    if result.upserted_id:
                        instance._id = result.upserted_id
                    else:
                        # Document already existed, get its _id
                        doc = collection.find_one({'key': instance.key})
                        if doc:
                            instance._id = doc.get('_id')
        
        def _delete_instance(self, instance):
            """Delete instance from MongoDB."""
            if instance._id:
                if isinstance(instance, User):
                    collection = get_collection(USERS_COLLECTION)
                    collection.delete_one({'_id': instance._id})
                elif isinstance(instance, AttendanceRecord):
                    collection = get_collection(ATTENDANCE_COLLECTION)
                    collection.delete_one({'_id': instance._id})
                elif isinstance(instance, Fine):
                    collection = get_collection(FINES_COLLECTION)
                    collection.delete_one({'_id': instance._id})
                elif isinstance(instance, Settings):
                    collection = get_collection(SETTINGS_COLLECTION)
                    collection.delete_one({'_id': instance._id})
        
        def rollback(self):
            """Rollback pending changes."""
            if hasattr(self, '_pending_add'):
                delattr(self, '_pending_add')
            if hasattr(self, '_pending_delete'):
                delattr(self, '_pending_delete')
    
    db_session = DBSession()
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise


class QueryBuilder:
    """Query builder that mimics SQLAlchemy query interface."""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self._filters = {}
        self._limit_value = None
    
    def filter(self, *args):
        """Add filter conditions."""
        # Handle filter() calls like: filter(User.telegram_id == 123)
        # or filter(AttendanceRecord.user_id == user.id)
        for condition in args:
            # Check if it's a QueryCondition (our custom column system)
            if isinstance(condition, QueryCondition):
                field_name = condition.field_name
                op = condition.operator
                value = condition.value
                
                # Convert value to appropriate type
                if field_name == 'user_id':
                    value = str(value)  # Ensure user_id is always a string
                elif field_name in ['date']:
                    # Convert date to datetime for MongoDB queries
                    if isinstance(value, date) and not isinstance(value, datetime):
                        value = datetime.combine(value, datetime.min.time()).replace(tzinfo=timezone.utc)
                    elif isinstance(value, datetime):
                        # Keep as datetime for MongoDB
                        pass
                
                if op == 'eq':
                    # Handle boolean comparisons (is_active == True)
                    if isinstance(value, bool):
                        self._filters[field_name] = value
                    else:
                        self._filters[field_name] = value
                elif op == 'ge':
                    self._filters[field_name] = {'$gte': value}
                elif op == 'le':
                    self._filters[field_name] = {'$lte': value}
                elif op == 'gt':
                    self._filters[field_name] = {'$gt': value}
                elif op == 'lt':
                    self._filters[field_name] = {'$lt': value}
                else:
                    self._filters[field_name] = value
            # Fallback for SQLAlchemy-style conditions (if any remain)
            elif hasattr(condition, 'left') and hasattr(condition, 'right'):
                left = condition.left
                right = condition.right
                if hasattr(left, 'key'):
                    field_name = left.key
                    # Convert value to appropriate type
                    if field_name == 'user_id':
                        right = str(right)
                    self._filters[field_name] = right
        return self
    
    def first(self):
        """Get first matching document."""
        collection = self._get_collection()
        query = self._build_query()
        doc = collection.find_one(query)
        if doc:
            return self.model_class.from_dict(doc)
        return None
    
    def all(self):
        """Get all matching documents."""
        collection = self._get_collection()
        query = self._build_query()
        cursor = collection.find(query)
        if self._limit_value:
            cursor = cursor.limit(self._limit_value)
        return [self.model_class.from_dict(doc) for doc in cursor]
    
    def limit(self, value):
        """Limit number of results."""
        self._limit_value = value
        return self
    
    def _get_collection(self):
        """Get the appropriate collection for the model."""
        if self.model_class == User:
            return get_collection(USERS_COLLECTION)
        elif self.model_class == AttendanceRecord:
            return get_collection(ATTENDANCE_COLLECTION)
        elif self.model_class == Fine:
            return get_collection(FINES_COLLECTION)
        elif self.model_class == Settings:
            return get_collection(SETTINGS_COLLECTION)
        else:
            raise ValueError(f"Unknown model class: {self.model_class}")
    
    def _build_query(self):
        """Build MongoDB query from filters."""
        query = {}
        for field_name, value in self._filters.items():
            if isinstance(value, dict) and any(k.startswith('$') for k in value.keys()):
                # Already a MongoDB operator query
                query[field_name] = value
            else:
                query[field_name] = value
        return query
