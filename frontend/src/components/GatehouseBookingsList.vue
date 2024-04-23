<template>
    <div>
      <h2 class="text-center mb-4">Gatehouse Bookings</h2>
      <div class="list-group">
        <a href="#" class="list-group-item list-group-item-action" 
           v-for="booking in bookings" :key="booking.id">
          <h5 class="mb-1">{{ booking.driver_name }}</h5>
          <p class="mb-1">Company: {{ booking.company }}</p>
          <p class="mb-1">Vehicle Registration: {{ booking.vehicle_registration }}</p>
          <small>Arrival Time: {{ new Date(booking.arrival_time).toLocaleString() }}</small>
          <button @click="updateBooking(booking.id)" class="btn btn-secondary btn-sm">Update</button>
          <button @click="cancelBooking(booking.id)" class="btn btn-warning btn-sm">Cancel</button>
          <button @click="deleteBooking(booking.id)" class="btn btn-danger btn-sm">Delete</button>
        </a>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        bookings: []
      };
    },
    created() {
      this.fetchBookings();
    },
    methods: {
      fetchBookings() {
        axios.get('/api/gatehouse-bookings/')
          .then(response => {
            this.bookings = response.data;
          })
          .catch(error => {
            console.error('Error fetching the bookings:', error);
          });
      },
      updateBooking(bookingId, updatedBooking) {
        // Handle booking update
        axios.put(`/api/gatehouse-bookings/${bookingId}/`, updatedBooking)
          .then(response => {
            const index = this.bookings.findIndex(booking => booking.id === bookingId);
            if (index !== -1) {
              this.$set(this.bookings, index, response.data);
              console.log('Booking updated successfully');
            }
          })
          .catch(error => {
            console.error('There was an error updating the booking:', error);
          });
      },
      cancelBooking(bookingId) {
        if (confirm('Are you sure you want to cancel this booking?')) {
          axios.put(`/api/gatehouse-bookings/${bookingId}/cancel/`)
            .then(() => {
              const booking = this.bookings.find(b => b.id === bookingId);
              if (booking) {
                booking.cancelled = true;
              }
              console.log('Booking cancelled successfully');
            })
            .catch(error => {
              console.error('Error cancelling the booking:', error);
            });
        }
      },
      deleteBooking(bookingId) {
        if (confirm('Are you sure you want to delete this booking?')) {
          axios.delete(`/api/gatehouse-bookings/${bookingId}/`)
            .then(() => {
              this.bookings = this.bookings.filter(booking => booking.id !== bookingId);
              console.log('Booking deleted successfully');
            })
            .catch(error => {
              console.error('Error deleting the booking:', error);
            });
        }
      }
    }
  }
  </script>
  
  <style scoped>
  /* Styles specific to this component */
  </style>
  