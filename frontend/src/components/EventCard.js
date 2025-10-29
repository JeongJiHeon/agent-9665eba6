import React from 'react';
import './EventCard.css';
import { format, parseISO } from 'date-fns';
import { ko } from 'date-fns/locale';

function EventCard({ event }) {
  const getEventTime = () => {
    try {
      const start = event.start?.dateTime || event.start?.date;
      const end = event.end?.dateTime || event.end?.date;
      
      if (!start) return '시간 미정';
      
      const startDate = parseISO(start);
      const endDate = end ? parseISO(end) : null;
      
      const startFormatted = format(startDate, 'M월 d일 (E) HH:mm', { locale: ko });
      const endFormatted = endDate ? format(endDate, 'HH:mm', { locale: ko }) : '';
      
      return endFormatted ? `${startFormatted} - ${endFormatted}` : startFormatted;
    } catch (error) {
      return '시간 정보 오류';
    }
  };

  const handleClick = () => {
    if (event.htmlLink) {
      window.open(event.htmlLink, '_blank');
    }
  };

  return (
    <div className="event-card" onClick={handleClick}>
      <div className="event-header">
        <h3>{event.summary || '제목 없음'}</h3>
        {event.location && (
          <span className="event-location">📍 {event.location}</span>
        )}
      </div>
      <div className="event-time">
        🕐 {getEventTime()}
      </div>
      {event.description && (
        <div className="event-description">
          {event.description}
        </div>
      )}
      {event.attendees && event.attendees.length > 0 && (
        <div className="event-attendees">
          👥 {event.attendees.length}명 참석
        </div>
      )}
    </div>
  );
}

export default EventCard;
